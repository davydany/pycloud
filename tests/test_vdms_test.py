#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pycloud` package."""


import unittest
from click.testing import CliRunner

from pycloud import pycloud
from pycloud import cli


class TestPyCloud(unittest.TestCase):
    """Tests for `pycloud` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.pycloud)
        assert result.exit_code == 0
        assert 'pycloud.cli.main' in result.output
        help_result = runner.invoke(cli.pycloud, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
