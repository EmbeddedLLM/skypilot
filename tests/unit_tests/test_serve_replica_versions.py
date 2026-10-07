"""Count-only `sky serve update` must keep reused replicas routable."""
import threading
import time
from unittest import mock

import pytest
import sqlalchemy

from sky.serve import replica_managers
from sky.serve import serve_state
from sky.serve import serve_utils
from sky.serve import service_spec
from sky.utils import common_utils
from sky.utils import yaml_utils

_SERVICE = 'svc'


def _yaml(replicas: int, run: str = 'python -m http.server 8080') -> str:
    return yaml_utils.dump_yaml_str({
        'service': {
            'readiness_probe': '/',
            'replicas': replicas
        },
        'resources': {
            'ports': 8080
        },
        'run': run,
        'file_mounts': {},
    })


def _add_version(version: int, yaml_content: str) -> None:
    serve_state.add_or_update_version(
        _SERVICE, version,
        service_spec.SkyServiceSpec.from_yaml_str(yaml_content), yaml_content)


@pytest.fixture
def manager(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    engine = sqlalchemy.create_engine(f'sqlite:///{tmp_path}/services.db')
    serve_state.create_table(engine)
    monkeypatch.setattr(serve_state._db_manager, '_engine', engine)
    # Pretend the replica is a launched, READY cluster.
    monkeypatch.setattr(replica_managers.ReplicaInfo, 'url',
                        property(lambda self: f'http://r{self.replica_id}'))
    monkeypatch.setattr(replica_managers.ReplicaInfo, 'status',
                        property(lambda self: serve_state.ReplicaStatus.READY))

    def make(mode: serve_utils.UpdateMode):
        serve_state.add_service(_SERVICE, 1, 'policy', 'resources',
                                'round_robin', serve_state.ServiceStatus.READY,
                                False, False, 1, 'entrypoint')
        _add_version(1, _yaml(1))
        info = replica_managers.ReplicaInfo(1, 'c1', '8080', False, None, 1,
                                            None)
        info.status_property.sky_launch_status = (
            common_utils.ProcessStatus.SUCCEEDED)
        info.status_property.first_ready_time = 1.0
        serve_state.add_or_update_replica(_SERVICE, 1, info)
        serve_utils.set_service_status_and_active_versions_from_replica(
            _SERVICE, serve_state.get_replica_infos(_SERVICE), mode)
        m = object.__new__(replica_managers.SkyPilotReplicaManager)
        m._service_name, m.latest_version, m._update_mode = _SERVICE, 1, mode
        m.lock, m._is_pool, m._uptime = threading.Lock(), False, 0
        return m

    return make


@pytest.mark.parametrize('mode', list(serve_utils.UpdateMode))
@pytest.mark.parametrize('run,expected_version', [
    ('python -m http.server 8080', 2),
    ('echo changed', 1),
])
def test_update_keeps_ready_replica_routable(manager, mode, run,
                                             expected_version):
    m = manager(mode)
    _add_version(2, _yaml(2, run))
    m.update_version(2, None, mode)
    assert serve_state.get_replica_infos(_SERVICE)[0].version == (
        expected_version)
    assert m.get_active_replica_urls() == ['http://r1']


def test_prober_does_not_revert_concurrent_relabel(manager):
    mode = serve_utils.UpdateMode.ROLLING
    m = manager(mode)
    _add_version(2, _yaml(2))
    probing = threading.Event()

    def slow_probe(self, *args):
        probing.set()
        time.sleep(0.5)
        return self, True, time.time()

    with mock.patch.object(replica_managers.ReplicaInfo, 'probe', slow_probe):
        prober = threading.Thread(target=m._probe_all_replicas)
        prober.start()
        assert probing.wait(5)
        m.update_version(2, None, mode)  # Lands while the probe is in flight.
        prober.join()

    info = serve_state.get_replica_infos(_SERVICE)[0]
    assert info.version == 2
    assert info.status_property.service_ready_now
