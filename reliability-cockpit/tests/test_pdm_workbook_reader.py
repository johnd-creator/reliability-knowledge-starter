from pathlib import Path
import tempfile,unittest,zipfile
from src.adapters.pdm_workbooks import Reader

def workbook(path,macro=False):
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    files={'[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
           '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
           'xl/workbook.xml':f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Synthetic" sheetId="1" r:id="rId1"/></sheets></workbook>',
           'xl/_rels/workbook.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
           'xl/worksheets/sheet1.xml':f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1"><f t="array" ref="A1:A2">1+1</f><v>2</v></c><c r="B1"><v>0</v></c></row><row r="2"><c r="A2"><v>2</v></c></row></sheetData></worksheet>'}
    with zipfile.ZipFile(path,'w') as z:
        for name,data in files.items():z.writestr(name,data)
        if macro:z.writestr('xl/vbaProject.bin',b'not executable; must be rejected')

class WorkbookReaderTest(unittest.TestCase):
    def test_array_formula_cache_not_misclassified_as_literal(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'source.xlsx';workbook(path);reader=Reader(path)
            try:
                self.assertTrue(reader.cell(0,'A1')['formula_present']);self.assertTrue(reader.cell(0,'A2')['formula_present']);self.assertEqual(reader.cell(0,'A2')['raw_value'],2);self.assertEqual(reader.cell(0,'A2')['cache_status'],'STORED_FORMULA_RESULT_NOT_RECALCULATED');self.assertEqual(reader.cell(0,'B1')['raw_value'],0);self.assertIsNone(reader.cell(0,'B2')['raw_value'])
            finally:reader.close()
    def test_macro_payload_rejected_before_loading(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'source.xlsx';workbook(path,True)
            with self.assertRaisesRegex(ValueError,'MACRO_WORKBOOK'):Reader(path)
    def test_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.xlsx';workbook(source);link=Path(d)/'link.xlsx';link.symlink_to(source)
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED'):Reader(link)
