.. SQL Mock documentation master file, created by
   sphinx-quickstart on Wed Nov  1 07:36:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SQL Mock's documentation!
====================================

The primary purpose of this library is to simplify the testing of SQL data models and queries by allowing users to mock input data and create tests for various scenarios. 
It provides a consistent and convenient way to test the execution of your query without the need to process a massive amount of data.

.. meta::
   :google-site-verification: ohDOHPn1YMLYMaWQpFmqQfPW_KRZXNK9Gq47pP57VQM

.. automodule:: sql_mock
    :members:
    :undoc-members:
    :show-inheritance:

.. toctree::
   :maxdepth: 3
   :caption: Getting Started

   getting_started/installation
   getting_started/quickstart
   faq

.. toctree::
   :maxdepth: 3
   :caption: Basic Usage   

   usage/defining_table_mocks
   usage/your_sql_query_to_test
   usage/result_assertion
   usage/examples

.. toctree::
   :maxdepth: 3
   :caption: Database Specifics   

   usage/bigquery/index
   usage/clickhouse/index

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   API Reference <modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
