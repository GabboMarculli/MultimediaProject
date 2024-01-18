package it.unipi.mircv.SearchEngine.structures;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;


/**
 * This class is used to represent the information inside the Lexicon.
 * 
 * 
 * @author Davide
 *
 */
public class LexiconRow{
	
	
	public static int LEXICON_ROW_SIZE=72;
	
	private String term;
	private int dft;
	private float maxTFIDF;
	private float maxBM25;
	private long docidOffset;
	private long frequencyOffset;
	private long blockOffset;
	private int numBlocks;
	
	/**
	 * Default constructor method.
	 */
	public LexiconRow() {
		this.term ="";
	}

	
	/**
	 * Constructor method:
	 * 
	 * 
	 * @param term - the term to store inside the lexicon
	 * @param dft - the document frequency of the term
	 * @param maxTFIDF - the TFIDF term upperbound.
	 * @param maxBM25 - the BM25 term upperbound.
	 * @param docidOffset - the starting offset of the docId file
	 * @param frequencyOffset - the starting offset of the freqs file
	 * @param blockOffset - the starting offset of the blocks file
	 * @param numBlocks - the total number of blocks of the term
	 */
	public LexiconRow(String term, int dft, float maxTFIDF, float maxBM25, long docidOffset, long frequencyOffset,
			long blockOffset, int numBlocks) {
		super();
		this.term = term;
		this.dft = dft;
		this.maxTFIDF = maxTFIDF;
		this.maxBM25 = maxBM25;
		this.docidOffset = docidOffset;
		this.frequencyOffset = frequencyOffset;
		this.blockOffset = blockOffset;
		this.numBlocks = numBlocks;
	}



	/**
	 * This function reads a lexicon row information in a specific position from an opened file.
	 * 
	 * @param file - the file to read a block descriptor
	 * @param offset - the position inside the file to read the lexicon row
	 * @return the offset position after reading
	 * @throws IOException
	 */
	public long readLexiconRowOnDiskFromOpenedFile(RandomAccessFile file, long offset) throws IOException {

		file.seek(offset);

        byte[] data = new byte[LexiconRow.LEXICON_ROW_SIZE];
        file.read(data);
        deserialize(data);

        return offset+LexiconRow.LEXICON_ROW_SIZE;
	}
	
	/**
	 * Method for interpreting the bytes in the data structures and populate the various fields.
	 * @param data
	 */
	private void deserialize(byte[] data) {
		
		ByteBuffer buffer = ByteBuffer.wrap(data);
		buffer.order(java.nio.ByteOrder.LITTLE_ENDIAN);
		
		this.term = new String(data, 0, 30);
		
		buffer.position(32);
		
		this.dft=buffer.getInt();
		this.numBlocks=buffer.getInt();
		this.maxTFIDF=buffer.getFloat();
		this.maxBM25=buffer.getFloat();
		this.docidOffset=buffer.getLong();
		this.frequencyOffset=buffer.getLong();
		this.blockOffset=buffer.getLong();
		
	}

	
	/** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
	
	public String getTerm() {
		return term;
	}

	public int getDft() {
		return dft;
	}


	public float getMaxTFIDF() {
		return maxTFIDF;
	}

	public float getMaxBM25() {
		return maxBM25;
	}

	public long getDocidOffset() {
		return docidOffset;
	}

	public long getFrequencyOffset() {
		return frequencyOffset;
	}

	public long getBlockOffset() {
		return blockOffset;
	}

	public int getNumBlocks() {
		return numBlocks;
	}
	
	
}