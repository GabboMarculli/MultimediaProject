package it.unipi.mircv.SearchEngine.handlers;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import it.unipi.mircv.SearchEngine.structures.BlockDescriptor;
import it.unipi.mircv.SearchEngine.structures.LexiconRow;
import it.unipi.mircv.SearchEngine.structures.Posting;


/**
 * The aim of this class is to handle the entire posting list that can be partially on memory and partial on disk.
 * This class exends the classical concept of the iterator in Java in order to hide all the details of the implementation
 * about loading other postings from disk.
 * 
 * @author Davide
 *
 */
public class PostingListHandler implements Iterator<Posting> {

	private LexiconRow lexiconElem;
	private List<BlockDescriptor> blockDescriptors;

	private Iterator<Posting> postingList;

	private RandomAccessFile fileDodIds;
	private RandomAccessFile fileFreqs;
	private RandomAccessFile fileBlocks;

	private boolean compressionMode;

	private int blockIndex;

	private Posting currentPosting;

	/** Constructor method: 
	 * 	
	 * @param lexiconElem - the lexicon element related that we want to read the posting list
	 * @param compressionMode - the modality in which the posting list is saved
	 * @param fileDodIds - the file from which loading the doc_ids of the posting list
	 * @param fileFreqs - the file from which loading the freqs of the posting list
	 * @param fileBlocks - the file from which loading the blocks of the posting list
	 * @throws IOException
	 */
	public PostingListHandler(LexiconRow lexiconElem, boolean compressionMode, RandomAccessFile fileDodIds,
			RandomAccessFile fileFreqs, RandomAccessFile fileBlocks) throws IOException {
		super();
		this.lexiconElem = lexiconElem;
		this.fileDodIds = fileDodIds;
		this.fileFreqs = fileFreqs;
		this.fileBlocks = fileBlocks;
		this.compressionMode = compressionMode;

		this.currentPosting = null;
		this.blockDescriptors = new ArrayList<BlockDescriptor>();
		
		/*  Saving immediately the information about all the blocks of a posting in memory.*/
		for (int i = 0; i < lexiconElem.getNumBlocks(); i++) {
			BlockDescriptor bd = new BlockDescriptor();
			bd.readBlockDescriptorOnDiskFromOpenedFile(fileBlocks,
					lexiconElem.getBlockOffset() + (BlockDescriptor.BLOCK_DESCRIPTOR_SIZE * i));
			blockDescriptors.add(bd);
		}

		this.blockIndex = 0;
		this.updatePostingList();

	}

   /**
	 * This method is called to check if the posting list handler has other postings available to be read.
	 * It first check in memory then in disk. When all the postings are read it returns false
	*/
	@Override
	public boolean hasNext() {

		if (postingList != null && postingList.hasNext()) {
			return true;
		}
		if (this.blockIndex < this.blockDescriptors.size() - 1) {
			this.blockIndex++;
			try {
				this.updatePostingList();
			} catch (IOException e) {
				e.printStackTrace();
			}
			return hasNext();
		}
		this.currentPosting = null;
		return false;
	}

	
   /**
	 *  This method returns the next element in the posting list updating the current element of posting.
	*/
	@Override
	public Posting next() {

		if (this.postingList != null) {
			this.currentPosting = postingList.next();
		}
		return this.currentPosting;
	}

	/**
	 * This function loads from disk the part of the posting list of the next block if available.
	 * @throws IOException
	 */
	private void updatePostingList() throws IOException {

		BlockDescriptor currentBlock = this.getCurrentBlock();
		if (currentBlock != null) {

			List<Posting> newpostingList = InvertedIndex.readFromFilePostingList(this.fileDodIds, this.fileFreqs,
					this.compressionMode, currentBlock.getOffsetDocIds(), currentBlock.getOffsetFreqs(),
					currentBlock.getNrPostings(), currentBlock.getDocIdsByteSize(), currentBlock.getFreqByteSize(),
					currentBlock.getMinDocId());
			this.postingList = newpostingList.iterator();

		}
	}
	/**
	 * This method returns the current block information for a specific lexicon term.
	 * @return the block descriptor object.
	 */
	public BlockDescriptor getCurrentBlock() {

		if (this.blockIndex < 0 || this.blockIndex > this.blockDescriptors.size()) {
			return null;
		}
		return this.blockDescriptors.get(this.blockIndex);

	}

	/**
	 * This method is used to skip the posting list to a specific element with greater or equal doc_id passed as argument.
	 * 
	 * @param docId, the docId to skip to
	 * @return the Posting with docId  greater or equal to docId to the passed
	 * @throws IOException
	 */
	public Posting nextGEQ(int docId) throws IOException {
		// Flag to check if the block has changed
		boolean blockChanged = false;

		// Move to the block with max_doc_id >= doc_id
		// Current block is null only if it's the first read
		while (getCurrentBlock() == null || getCurrentBlock().getMaxDocId() < docId) {
			// End of list, return null
			if (this.blockIndex >= this.blockDescriptors.size() - 1) {
				this.currentPosting = null;
				return null;
			}

			this.blockIndex++;
			blockChanged = true;
		}

		if (getCurrentBlock() != null)
			updatePostingList();

		// Block changed, load postings and update iterator
		if (blockChanged)
			// Remove previous postings
			currentPosting = postingList.hasNext() ? postingList.next() : null;

		// Move to the first posting greater or equal than docId and return it
		while (currentPosting != null && currentPosting.getDocId() < docId)
			currentPosting = postingList.hasNext() ? postingList.next() : null;

		return currentPosting;
	}

	
	/** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
	
	public LexiconRow getLexiconElem() {
		return lexiconElem;
	}
	
	public Float getTermUpperboundTFIDF() {
		if (lexiconElem!=null) {
			return lexiconElem.getMaxTFIDF();
		}
		return null;
	}

	public Float getTermUpperboundBM25() {
		if (lexiconElem!=null) {
			return lexiconElem.getMaxBM25();
		}
		return null;
	}
	
	
	public List<BlockDescriptor> getBlockDescriptors() {
		return blockDescriptors;
	}

	public Iterator<Posting> getPostingList() {
		return postingList;
	}

	public RandomAccessFile getFileDodIds() {
		return fileDodIds;
	}

	public RandomAccessFile getFileFreqs() {
		return fileFreqs;
	}

	public RandomAccessFile getFileBlocks() {
		return fileBlocks;
	}

	public boolean isCompressionMode() {
		return compressionMode;
	}

	public int getBlockIndex() {
		return blockIndex;
	}

	public Posting getCurrentPosting() {
		return currentPosting;
	}
	
	
}
