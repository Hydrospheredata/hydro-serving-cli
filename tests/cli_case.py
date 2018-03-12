import unittest

import os
import shutil

from click.testing import CliRunner

from hydroserving.cli import hs_cli


class CLICase(unittest.TestCase):
    def test_incorrect_status(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(hs_cli, ["status"])
            assert result.exit_code == -1
            assert "Directory doesn't have a serving metadata" in result.output

    def test_correct_status(self):
        runner = CliRunner()
        old_cwd = os.getcwd()
        os.chdir("examples/local_dev")
        result = runner.invoke(hs_cli, ["status"])
        assert result.exit_code == 0
        assert "Detected a model: example_script" in result.output
        os.chdir(old_cwd)

    def test_pack(self):
        runner = CliRunner()
        old_cwd = os.getcwd()
        os.chdir("examples/local_dev")
        result = runner.invoke(hs_cli, ["pack"])
        print(result.output)
        assert result.exit_code == 0
        assert "Packing the model" in result.output
        assert "Done" in result.output
        assert os.path.exists("target/model/files")
        assert os.path.exists("target/model/contract.protobin")
        shutil.rmtree("target")
        os.chdir(old_cwd)

    def test_assembly(self):
        runner = CliRunner()
        old_cwd = os.getcwd()
        os.chdir("examples/local_dev")
        result = runner.invoke(hs_cli, ["assemble"])
        print(result.output)
        assert result.exit_code == 0
        assert "Assembling the model" in result.output
        assert "Done" in result.output
        assert os.path.exists("target/example_script.tar.gz")
        shutil.rmtree("target")
        os.chdir(old_cwd)

    def test_upload(self):
        pass


if __name__ == "__main__":
    unittest.main()
