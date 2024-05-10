"""Unit tests for Docs Agent CLI."""

import unittest


class DocsAgentCLIUnitTest(unittest.TestCase):
  def test_basic(self):
    self.assertEqual('hello'.upper(), 'HELLO')

if __name__ == "__main__":
  unittest.main()
