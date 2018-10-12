# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 16:52:02 2018

@author: maojin.xia
"""

from scrapy.conf import settings
from scrapy.contrib.exporter import CsvItemExporter
import io

class MyProjectCsvItemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):
        delimiter = settings.get('CSV_DELIMITER', ',')
        kwargs['delimiter'] = delimiter
        fields_to_export = settings.get('FIELDS_TO_EXPORT', [])
        if fields_to_export :
            kwargs['fields_to_export'] = fields_to_export

        super(MyProjectCsvItemExporter, self).__init__(*args, **kwargs)

