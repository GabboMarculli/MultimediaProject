package Test;

import static Test.Utils.createFileIfNotExists;
import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.nio.file.Path;


import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import it.unipi.mircv.SearchEngine.handlers.Lexicon;
import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;
import it.unipi.mircv.SearchEngine.structures.LexiconRow;

class LexiconTest {

    private Lexicon lexicon;
    private CollectionStatistics collectionStatistics;
    private RandomAccessFile fileLexicon;

    @Test
    public void testLexiconFunctionalities() throws IOException{
        LexiconRow lexRow = new LexiconRow();

        RandomAccessFile fileLexicon= new RandomAccessFile("D:\\QueryProcessing\\SearchEngine\\lexicon.bin", "r");
        CollectionStatistics cs= new CollectionStatistics("D:\\QueryProcessing\\SearchEngine\\collection_statistics.txt");
        lexicon = new Lexicon(512, false,fileLexicon, cs);

        lexRow = lexicon.getLexiconRowTerm("0");
        assertEquals(lexRow.getDft(), 194228);
        assertEquals(lexRow.getMaxTFIDF(), 18.830875396728516);
        assertEquals(lexRow.getMaxBM25(), 1.5869719982147217);
        assertEquals(lexRow.getNumBlocks(), 441);
        assertEquals(lexRow.getBlockOffset(), 0);
        assertEquals(lexRow.getDocidOffset(), 0);
        assertEquals(lexRow.getFrequencyOffset(), 0);

        lexRow = lexicon.getLexiconRowTerm("eofiwbldvknewovldnskvd");
        assertEquals(lexRow, null);


    }


}
