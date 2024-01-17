package it.unipi.mircv.SearchEngine.utilities;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


/**
 * This class is used in the project to implement integer decompression.
 * It contains static methods for uncompressing integer / list of integers.
 * There are three kind of implementation of compression algorithms:
 *    - Unary Compression, it is used for term_freq posting list compression.
 *    - Variable Byte Compression, it is used for compressing a single gap of a doc_id inside the d-gap list.
 *    - D-Gap Compression, it is used to compress a list of docIds gaps. 
 *    
 * @author Davide
 */
public class Decompression {
	
	/**
	 * Given a list of bytes and a total number of integers to read, it uncompresses the list of bytes and 
     * decode the corresponding integers returning as a list of integers.
     * 
	 * @param buffer the input buffer of bytes to be processed
	 * @param totalIntegers the total number of integer to uncompresses
	 * @return the list of integers uncompressed
	 */
	public static List<Integer> unaryDecompressionIntegerList(ByteBuffer buffer,int totalIntegers){
		
        List<Integer> uncompressedList = new ArrayList<>();

        int maxMask = 0b11111111;
        int currentInteger = 0;
        
        byte[] binaryData = buffer.array();

        
        for (int i = 0; i < binaryData.length; i++) {
        	
        	byte data=binaryData[i];
        	
        	// First check if the entire byte is set to '1', to speed up decompression.
            if (data == maxMask) {
                currentInteger += 8;
            } else {
                // This is the case where at least a '0' is present inside the byte.
                for (int index = 0; index < 8; index++) {
                    if ((data & (1 << (7 - index))) == 0) {
                        // Found '0', add decompressed integer to the list.
                        uncompressedList.add(currentInteger + 1);

                        // Check if finished reading all integers.
                        if (uncompressedList.size() == totalIntegers) {
                            break;
                        }
                        currentInteger = 0;
                    } else {
                        currentInteger += 1;
                    }
                }
            }
        }
        	
        return uncompressedList;
	}
	
	/**
	 * Given a list of bytes, it uncompresses that list and decode 
	 * the corresponding integers returning the result in a list.
	 * 
	 * @param buffer the input buffer of bytes to be processed
	 * @return the list of decompressed integers
	 */
	public static List<Integer> variableByteDecompressionIntegerList(ByteBuffer buffer){
		
		 List<Integer> uncompressedList = new ArrayList<>();
	     int currentInteger = 0;
	     
	     byte[] binaryData = buffer.array();
	     
	     for (int index = 0; index < binaryData.length; index++) {
	            int mask = 0b01111111;
	            byte data = binaryData[index];

	            if ((data & (1 << 7)) != 0) {
	                // Most significant bit set to '1', continuation byte.
	                data = (byte) (data & mask);
	                currentInteger = currentInteger * 128 + data;
	            } else {
	                // Most significant bit set to '0', stop byte.
	                if (index != 0) {
	                    uncompressedList.add(currentInteger);
	                }

	                currentInteger = data;
	            }
	        }

        // Append the last decompressed integer
        if (binaryData.length != 0) {
            uncompressedList.add(currentInteger);
        }
		return uncompressedList;
	}
	
	/**
	 * Given a list of bytes, it uncompresses that list using variable_byte_compression.
	 * The list obtained is the list of d-gaps so it is converted in actual docIds numbers
	 * and it is returned.
	 * 
	 * @param buffer
	 * @param startingPoint
	 * @return
	 */
	public static List<Integer> DGapDecompression (ByteBuffer buffer, int startingPoint){
		
		List<Integer> dGapList=variableByteDecompressionIntegerList(buffer);
		
		if (dGapList.size()==1) {
			return Arrays.asList(startingPoint);
		}
		

        List<Integer> uncompressedList = new ArrayList<>();
        uncompressedList.add(startingPoint);

        for (int gap : dGapList.subList(1, dGapList.size())) {
            startingPoint += gap;
            uncompressedList.add(startingPoint);
        }

        return uncompressedList;
	}
	
}
