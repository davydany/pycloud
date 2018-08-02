#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `vdms_test` package."""


import unittest
from click.testing import CliRunner

from vdms_test import vdms_test
from vdms_test import cli


class TestVdms_test(unittest.TestCase):
    """Tests for `vdms_test` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.vdms_test)
        assert result.exit_code == 0
        assert 'vdms_test.cli.main' in result.output
        help_result = runner.invoke(cli.vdms_test, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
