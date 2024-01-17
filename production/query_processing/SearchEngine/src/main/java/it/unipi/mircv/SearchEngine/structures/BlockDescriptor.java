package it.unipi.mircv.SearchEngine.structures;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;

/**
 *  This class is used to represent the block of a posting list to be saved on disk.
 *  It contains information about the starting offset of doc_ids and frequencies of the representing block,
 *  the number of posting inside, the effective occupied size of the docs and freqs.
 *  In addition it contains information about the minium and maxium doc_id contained.
 *  The min doc_id is used during compression/decompression thought d-gap variable encoding to know from
 *  what document to start decompressing.
 *  The max doc id is used instead for the implementation of nextGeq avoiding to read blocks that for sure 
 *  are not of our interest in a specific moment.
 * 
 *  @author Davide
 */
public class BlockDescriptor {
	
	public static int BLOCK_DESCRIPTOR_SIZE=36;
	
	private long offsetDocIds;
	private long offsetFreqs;
	private int nrPostings;
	private int docIdsByteSize;
	private int freqByteSize;
	private int minDocId;
	private int maxDocId;
	
	/**
	 * Default constructor method.
	 */
	public BlockDescriptor() {
		super();
	}
	
	/**
	 * Constructor method: 
	 * 
	 * @param offset_doc_ids - the starting offset of the doc_ids file
	 * @param offset_freqs - the starting offset of the freqs file
	 * @param nr_postings - the number of posting contained in the block
	 * @param doc_ids_bytes_size - the dimension in byte of the doc_ids contained in the block 
	 * @param freq_bytes_size - the dimension in byte of the freqs contained in the block 
	 * @param min_doc_id - the minimum doc id contained in the block, used for d-gap decompression
	 * @param max_doc_id - the maximum doc id contained in the block, used for skipping to next block
	 */
	public BlockDescriptor(long offset_doc_ids, long offset_freqs, int nr_postings, int doc_ids_bytes_size,
			int freq_bytes_size, int min_doc_id, int max_doc_id) {
		super();
		this.offsetDocIds = offset_doc_ids;
		this.offsetFreqs = offset_freqs;
		this.nrPostings = nr_postings;
		this.docIdsByteSize = doc_ids_bytes_size;
		this.freqByteSize = freq_bytes_size;
		this.minDocId = min_doc_id;
		this.maxDocId = max_doc_id;
	}
	
	/**
	 * This function reads a block descriptor information in a specific position from an opened file.
	 * 
	 * @param file - the file to read a block descriptor
	 * @param offset - the position inside the file to read the block descriptor
	 * @return the offset position after reading
	 * @throws IOException
	 */
	public long readBlockDescriptorOnDiskFromOpenedFile(RandomAccessFile file,long offset) throws IOException {
		
		 file.seek(offset);
		
		 byte[] data = new byte[BLOCK_DESCRIPTOR_SIZE];
         file.read(data);
         
         deserialize(data);
		
		return offset+BLOCK_DESCRIPTOR_SIZE;
	}
	
	
	/**
	 * Method for interpreting the bytes in the data structures and populate the various fields.
	 * @param data the array of bytes
	 */
	private void deserialize(byte[] data) {
		
		ByteBuffer buffer = ByteBuffer.wrap(data);
		buffer.order(java.nio.ByteOrder.LITTLE_ENDIAN);
		
		this.offsetDocIds=buffer.getLong();
		this.offsetFreqs=buffer.getLong();
		this.nrPostings=buffer.getInt();
		
		this.docIdsByteSize=buffer.getInt();
		this.freqByteSize=buffer.getInt();
		this.minDocId=buffer.getInt();
		this.maxDocId=buffer.getInt();
		
	}

	/** Next all the getter methods that expose the private variables and allows to handle them in a "safty way".*/
	
	public long getOffsetDocIds() {
		return offsetDocIds;
	}

	public long getOffsetFreqs() {
		return offsetFreqs;
	}

	public int getNrPostings() {
		return nrPostings;
	}

	public int getDocIdsByteSize() {
		return docIdsByteSize;
	}

	public int getFreqByteSize() {
		return freqByteSize;
	}

	public int getMinDocId() {
		return minDocId;
	}

	public int getMaxDocId() {
		return maxDocId;
	}

	/*
	   Used only for test scope
	*/
	public byte[] serialize() {
	   ByteBuffer buffer = ByteBuffer.allocate(BLOCK_DESCRIPTOR_SIZE);
	   buffer.order(java.nio.ByteOrder.LITTLE_ENDIAN);

	   buffer.putLong(offsetDocIds);
	   buffer.putLong(offsetFreqs);
	   buffer.putInt(nrPostings);
	   buffer.putInt(docIdsByteSize);
	   buffer.putInt(freqByteSize);
	   buffer.putInt(minDocId);
	   buffer.putInt(maxDocId);

	   return buffer.array();
	}
	
	
}
