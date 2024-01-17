package it.unipi.mircv.SearchEngine.structures;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * This class represent a generic information contained inside a posting.
 *
 * @author Davide
 *
 */
public class Posting {

	private int docId;
	private int frequency;
	
	/**
	 * Constructor method:
	 * 
	 * @param docId - the unique identification of a document
	 * @param frequency - the number of times a specific term is present inside a document with docId
	 */
	public Posting(int docId, int frequency) {
		super();
		this.docId = docId;
		this.frequency = frequency;
	}
	
	public static List<Posting> createPostingList(List<Integer>docIds,List<Integer>freqs){
		
		/*List<Posting> returnList=new ArrayList<Posting>();
		for (int i=0;i<docIds.size();i++) {
			returnList.add(new Posting(docIds.get(i), freqs.get(i)));
		}
		return returnList;*/
		
		//JAVA 8 
		return IntStream.range(0, docIds.size()).mapToObj(i -> new Posting(docIds.get(i), freqs.get(i))).collect(Collectors.toList());
	}
	
	@Override
	public String toString() {
		return "Posting [docId=" + docId + ", frequency=" + frequency + "]";
	}

	/** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
	
	public int getDocId() {
		return docId;
	}

	public int getFrequency() {
		return frequency;
	}

	
}
