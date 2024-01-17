package Test;

import static org.junit.jupiter.api.Assertions.assertEquals;


import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.structures.CollectionStatistics;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class CollectionStatisticsTest {
    String TEST_FILE_PATH = "collectionStatisticsTest.bin";

    @AfterEach
    public void tearDown() throws IOException {
        // Delete the test file after each test
        Files.deleteIfExists(Paths.get(TEST_FILE_PATH));
    }

    @Test
    public void testGetAverageDocumentLength() throws IOException {
        // Create a temporary file for testing
        Utils.createFileIfNotExists(TEST_FILE_PATH);

        try {
            // Write some sample statistics to the temporary file
            writeSampleStatistics(TEST_FILE_PATH);

            // Create an instance of CollectionStatistics using the temporary file
            CollectionStatistics collectionStatistics = new CollectionStatistics(TEST_FILE_PATH);

            // Assert the result
            assertEquals(3, collectionStatistics.getNumDocuments());
            assertEquals(30, collectionStatistics.getSumDocumentLengths());
            assertEquals(20, collectionStatistics.getNumDistinctTerms());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void writeSampleStatistics(String TEST_FILE_PATH) throws IOException {
        // Write sample statistics to the file
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(TEST_FILE_PATH))) {
            bw.write("Document Index Size: 3");
            bw.newLine();
            bw.write("Vocabulary Size: 20");
            bw.newLine();
            bw.write("Sum Document length: 30");
        }
    }
}

