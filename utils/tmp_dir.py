import pathlib


class TmpDir:
    """
    一个表示临时目录的类。该目录在对象销毁时被删除。

    属性:
        tmp_file_path (pathlib.Path): 临时文件的路径。
    """

    def __init__(self):
        """
        初始化TmpDir类的实例，如果临时目录不存在，则创建它。
        """
        self.tmp_file_path = pathlib.Path("./tmp/")
        self._create_tmp_directory()

    def _create_tmp_directory(self):
        """
        创建临时目录，如果它还不存在。
        """
        if not self.tmp_file_path.exists():
            self.tmp_file_path.mkdir(parents=True)

    def path(self):
        """
        返回临时目录的路径。

        :return: 临时目录的路径字符串。
        """
        return str(self.tmp_file_path) + "/"
