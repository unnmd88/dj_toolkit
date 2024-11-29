from unittest import TestCase, main
from toolkit.sdp_lib.controller_management import BaseUG405
import asyncio


class TestBaseUG405(TestCase):
    def setUp(self) -> None:
        self.host = BaseUG405('10.45.154.11', host_id=2, scn='CO1111')

    def test_get_utcType2OperationMode(self):
        self.assertIn(int(asyncio.run(self.host.get_utcType2OperationMode())[0]), range(1, 3))


if __name__ == '__main__':
    main()
