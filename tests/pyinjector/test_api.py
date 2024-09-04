from pytest import mark

from pyinjector.api import self_relative_path


@mark.parametrize('library_path,process_root,expected', [
    (b'/tmp/some/lib.so', '', b'/tmp/some/lib.so'),
    (b'/tmp/some/lib.so', b'', b'/tmp/some/lib.so'),
    (b'/tmp/some/lib.so', '/proc/123/root', b'/proc/123/root/tmp/some/lib.so'),
    (b'/tmp/some/lib.so', '/proc/123/root/', b'/proc/123/root/tmp/some/lib.so'),
    (b'tmp/some/lib.so', '/proc/123/root', b'/proc/123/root/tmp/some/lib.so'),
    (b'tmp/some/lib.so', '/proc/123/root/', b'/proc/123/root/tmp/some/lib.so'),
])
def test_self_relative_path(library_path, process_root, expected):

    assert self_relative_path(library_path, process_root) == expected
