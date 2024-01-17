package it.unipi.mircv.SearchEngine.handlers;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;

import it.unipi.mircv.SearchEngine.structures.Posting;
import it.unipi.mircv.SearchEngine.utilities.Decompression;


/**
 * This class is used to manage an InvertedIndex. 
 * In this part of the project it is not necessary to manage insertion/modification of postings; 
 * this part is already implemented in Python during the indexing.
 * 
 * The idea is to use this class to load from disk the prepared Inverted Index data structure as demanded.
 * 
 * @author Davide
 *
 */
public class InvertedIndex {
	
	
	/**
	 * This static method is able to load a list of postings related to a specific term from Disk.
	 * With this method it is possible to read 'a number of postings' of a posting list from 2 distinct files:
     * One file contains the saved docIds and the other contains the saved frequencies.
	 * 
	 * @param fileDodIds - the file where doc_ids are saved
	 * @param fileFreq - the file where frequencies are saved
	 * @param compressionMode - to specify if the bytes to be read must be decompressed or not
	 * @param offsetDocIds - the start offset position for reading the list of doc_ids
	 * @param offsetFreqs - the start offset position for reading the list of frequency
	 * @param nrPostings - indicates the number of elements to be read
	 * @param docIdsByteSize - used only if compressionMode is True instead of nrPostings and indicates the dimension in bytes of doc_ids to be read
	 * @param freqsByteSize - used only if compressionMode is True instead of nrPostings and indicates the dimension in bytes of freqs to be read
	 * @param minDocId - used only if compressionMode is True and indicates the number of elements to be read
	 * @return a posting list containing docIds and Freqs from the files
	 * @throws IOException
	 */
	public static List<Posting> readFromFilePostingList(RandomAccessFile fileDodIds,RandomAccessFile fileFreq,boolean compressionMode,
			long offsetDocIds,long offsetFreqs,int nrPostings,int docIdsByteSize, int freqsByteSize,int minDocId) throws IOException {
		
		
		fileDodIds.seek(offsetDocIds);
		fileFreq.seek(offsetFreqs);
		
		List<Integer> listDocIds=new ArrayList<Integer>();
		List<Integer> listFreqs=new ArrayList<Integer>();
		
		byte[] dataDocIds = new byte[docIdsByteSize];
		byte[] dataFreqs = new byte[freqsByteSize];
		
		fileDodIds.read(dataDocIds);
		fileFreq.read(dataFreqs);
		
		ByteBuffer bufferDocIds = ByteBuffer.wrap(dataDocIds);
		bufferDocIds.order(java.nio.ByteOrder.BIG_ENDIAN);
		
		ByteBuffer bufferFreqs = ByteBuffer.wrap(dataFreqs);
		bufferFreqs.order(java.nio.ByteOrder.BIG_ENDIAN);
		
		if (!compressionMode) {
			 while (bufferDocIds.hasRemaining()) {
				 listDocIds.add(bufferDocIds.getInt());
			 }

			 while (bufferFreqs.hasRemaining()) {
				 listFreqs.add(bufferFreqs.getInt());
			 }
		}
		else {
			listFreqs=Decompression.unaryDecompressionIntegerList(bufferFreqs, nrPostings);
			listDocIds=Decompression.DGapDecompression(bufferDocIds, minDocId);	
		}
		
		return Posting.createPostingList(listDocIds,listFreqs);
	}

}

