package Test;


import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.structures.DocumentIndexRow;

import java.io.IOException;
import java.io.RandomAccessFile;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DocumentIndexRowTest {

    @Test
    void testReadDocIndexRowOnDisk() throws IOException {
        RandomAccessFile docIndexFile = new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\document_index.bin", "rw");

        DocumentIndexRow readRow = new DocumentIndexRow();
        readRow.readDocIndexRowOnDisk(docIndexFile, 28282*readRow.SIZE_DOC_INDEX_ROW);

        assertEquals("28282", readRow.getDocNo().trim());
        assertEquals(58, readRow.getDocumentLength());

        readRow.readDocIndexRowOnDisk(docIndexFile, 4730095*readRow.SIZE_DOC_INDEX_ROW);

        assertEquals("4730095", readRow.getDocNo().trim());
        assertEquals(59, readRow.getDocumentLength());
    }
}

