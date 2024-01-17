package it.unipi.mircv.SearchEngine.handlers;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import it.unipi.mircv.SearchEngine.structures.DocumentIndexRow;

/**
 * This class is used as cache to store the entire document index in main
 * memory. This operation is done at the begin.
 * 
 * @author Davide
 *
 */
public class DocumentIndex {

	public HashMap<Long, Integer> cacheDocumentIndex;

	public DocumentIndex() {
		super();
		this.cacheDocumentIndex = new HashMap<Long, Integer>();
	}

	public void initCache(String pathDocIndex, int numDocs) throws IOException, InterruptedException, ExecutionException {

// Not parallelized version.
//		DocumentIndexRow doc = new DocumentIndexRow();
//
//		for (int offset = 0; offset < numDocs; offset++) {
//			doc.readDocIndexRowOnDisk(docIndexFile, offset * DocumentIndexRow.SIZE_DOC_INDEX_ROW);
//			cacheDocumentIndex.put(doc.getDocId(), doc.getDocumentLength());
//		}
		
		cacheDocumentIndex=readInParallel(pathDocIndex,numDocs);
	}

	public static HashMap<Long, Integer> readInParallel(String filePath, int totDocCollection)
			throws InterruptedException, ExecutionException {

		int MAXPROCESSORS = Math.min(10, Runtime.getRuntime().availableProcessors());// Tested with 10, having 12 as max CPUs.
		
		ExecutorService executor = Executors.newFixedThreadPool(MAXPROCESSORS);
		HashMap<Long, Integer> returnMap = new HashMap<Long, Integer>();

		try {

			int numberofDocs = totDocCollection / MAXPROCESSORS;

			List<Long> docsStart = new ArrayList<Long>();
			List<Long> docsEnd = new ArrayList<Long>();

			long docStart = 0;
			long docEnd = 0;
			for (int i = 0; i < MAXPROCESSORS; i++) {
				docStart = i * numberofDocs;
				docEnd = (i + 1) * numberofDocs;

				docsStart.add(docStart);
				docsEnd.add(docEnd);
			}
			if (docEnd != totDocCollection) {
				docsEnd.set(docsEnd.size() - 1, docsEnd.get(docsEnd.size() - 1) + (totDocCollection - docEnd));
			}

			List<Callable<HashMap<Long, Integer>>> listCallable = new ArrayList<Callable<HashMap<Long, Integer>>>();

			for (int i = 0; i < MAXPROCESSORS; i++) {
				final int currenIndex = i;
				Callable<HashMap<Long, Integer>> readTaskN = () -> readFile(filePath, docsStart.get(currenIndex),
						docsEnd.get(currenIndex));
				listCallable.add(readTaskN);
			}

			List<Future<HashMap<Long, Integer>>> futureList = new ArrayList<Future<HashMap<Long, Integer>>>();

			for (Iterator<Callable<HashMap<Long, Integer>>> iterator = listCallable.iterator(); iterator.hasNext();) {
				Callable<HashMap<Long, Integer>> callable = (Callable<HashMap<Long, Integer>>) iterator.next();
				Future<HashMap<Long, Integer>> futurePart = executor.submit(callable);
				futureList.add(futurePart);
			}

			for (Iterator<Future<HashMap<Long, Integer>>> iterator = futureList.iterator(); iterator.hasNext();) {
				Future<HashMap<Long, Integer>> future = (Future<HashMap<Long, Integer>>) iterator.next();
				HashMap<Long, Integer> ris = future.get();
				returnMap.putAll(ris);
			}

			return returnMap;
		} finally {
			executor.shutdown();
		}
	}

	private static HashMap<Long, Integer> readFile(String filePath, long docStart, long docEnd) throws IOException {

		HashMap<Long, Integer> mappa = new HashMap<Long, Integer>();
		DocumentIndexRow docIndRow = new DocumentIndexRow();

		try (RandomAccessFile file = new RandomAccessFile(filePath, "r")) {
			while (docStart < docEnd) {
				docIndRow.readDocIndexRowOnDisk(file, docStart * DocumentIndexRow.SIZE_DOC_INDEX_ROW);
				mappa.put(docStart, docIndRow.getDocumentLength());
				docStart += 1;
			}
		}
		return mappa;
	}
	
	
	public HashMap<Long, Integer> getCacheDocumentIndex() {
		return cacheDocumentIndex;
	}
	

}
