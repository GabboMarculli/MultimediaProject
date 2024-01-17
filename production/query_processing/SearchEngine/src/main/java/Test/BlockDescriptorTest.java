package Test;

import static Test.Utils.createFileIfNotExists;
import static org.junit.jupiter.api.Assertions.assertEquals;


import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.structures.BlockDescriptor;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;


public class BlockDescriptorTest {

    private static final String TEST_FILE_PATH = "block_descriptor_test_file.bin";


    @BeforeEach
    public void setUp() throws IOException {
        createFileIfNotExists(TEST_FILE_PATH);
        // Create a test file with some data
        try (RandomAccessFile file = new RandomAccessFile(TEST_FILE_PATH, "rw")) {
            // Write a BlockDescriptor to the file
            BlockDescriptor blockDescriptor = new BlockDescriptor(100, 200, 50, 30, 40, 10, 90);
            byte[] serializedData = blockDescriptor.serialize();
            file.write(serializedData);
        }
    }

    @AfterEach
    public void tearDown() throws IOException {
        // Delete the test file after each test
        Files.deleteIfExists(Paths.get(TEST_FILE_PATH));
    }

    @Test
    public void testReadBlockDescriptorOnDiskFromOpenedFile() throws IOException {
        try (RandomAccessFile file = new RandomAccessFile(TEST_FILE_PATH, "r")) {
            // Read the BlockDescriptor from the file
            BlockDescriptor blockDescriptor = new BlockDescriptor();
            blockDescriptor.readBlockDescriptorOnDiskFromOpenedFile(file, 0);

            // Check if the values match the expected values
            assertEquals(100, blockDescriptor.getOffsetDocIds());
            assertEquals(200, blockDescriptor.getOffsetFreqs());
            assertEquals(50, blockDescriptor.getNrPostings());
            assertEquals(30, blockDescriptor.getDocIdsByteSize());
            assertEquals(40, blockDescriptor.getFreqByteSize());
            assertEquals(10, blockDescriptor.getMinDocId());
            assertEquals(90, blockDescriptor.getMaxDocId());
        }
    }
}

