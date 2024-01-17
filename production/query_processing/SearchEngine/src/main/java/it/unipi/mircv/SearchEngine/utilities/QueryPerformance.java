package it.unipi.mircv.SearchEngine.utilities;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import it.unipi.mircv.SearchEngine.handlers.QueryProcesser;
import it.unipi.mircv.SearchEngine.utilities.Scoring.ObjScore;

/**
 * This class represents a performance evaluator for a search engine system. It
 * includes methods for loading queries and relevance data, computing various
 * evaluation metrics such as precision, average precision, recall, and
 * discounted cumulative gain. The class is designed to work with a
 * QueryProcessor to evaluate the effectiveness of the search engine's results
 * based on relevance data and scoring functions. The class provides
 * functionality to measure and report metrics for multiple queries, offering
 * insights into the system's retrieval performance.
 *
 * @author Gabriele
 */
public class QueryPerformance {

	private QueryProcesser queryProcesser;

	/**
	 * 
	 * @param pathDocIndex                   - The path for the document index.
	 * @param pathLexicon                    - The path for the lexicon file.
	 * @param pathCollectionStatistics       - The path for the Collection
	 *                                       Statistics.
	 * @param pathDocIds                     - The path for the file containing
	 *                                       document IDs of the postings lists.
	 * @param pathFreqs                      - The path for for the file containing
	 *                                       block information.
	 * @param pathBlocks                     - The path for the file containing
	 *                                       block information.
	 * @param stopWordsPath                  - The path for the stop word list.
	 * @param useStemmingAndStopWordsRemoval - Flag indicating if remove or not stop
	 *                                       words and do stemming on query.
	 * @param compressionMode                - If using compression or not
	 * @param useCache                       - If using the cache or not
	 * @param kResults                       - The number of top documents to
	 *                                       retrieve for each query.
	 * @throws Exception
	 */
	public QueryPerformance(String pathDocIndex, String pathLexicon, String pathCollectionStatistics, String pathDocIds,
			String pathFreqs, String pathBlocks, String stopWordsPath, boolean useStemmingAndStopWordsRemoval,
			boolean compressionMode, boolean useCache, int kResults

	) throws Exception {

		this.queryProcesser = new QueryProcesser(pathDocIndex, pathLexicon, pathCollectionStatistics, pathDocIds,
				pathFreqs, pathBlocks, stopWordsPath, useStemmingAndStopWordsRemoval, compressionMode, useCache,
				kResults);
	}

	/**
	 * Load queries from a file and return a map of query IDs to query texts.
	 *
	 * @param filePath The path to the file containing queries.
	 * @return A map of query IDs to query texts.
	 */
	public Map<Integer, String> loadQueries(String filePath) {
		Map<Integer, String> queries = new HashMap<>();

		try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
			String line;
			while ((line = reader.readLine()) != null) {
				String[] parts = line.split("\t");
				int queryId = Integer.parseInt(parts[0]);
				String queryText = parts[1];
				queries.put(queryId, queryText);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		return queries;
	}

	/**
	 * Load relevance data from a file and return a map of query IDs to a map of
	 * document IDs and relevance scores.
	 *
	 * @param filePath The path to the file containing relevance data.
	 * @return A map of query IDs to a map of document IDs and relevance scores.
	 */
	public Map<Integer, Map<Integer, Integer>> loadRelevance(String filePath) {
		Map<Integer, Map<Integer, Integer>> relevance = new HashMap<>();

		try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
			String line;
			while ((line = reader.readLine()) != null) {
				String[] parts = line.split(" ");
				int queryId = Integer.parseInt(parts[0]);
				int documentId = Integer.parseInt(parts[2]);
				int relevanceScore = Integer.parseInt(parts[3]);

				relevance.computeIfAbsent(queryId, k -> new HashMap<>()).put(documentId, relevanceScore);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		return relevance;
	}

	/**
	 * Calculate precision at k for a list of query results. The precision at k is
	 * the ratio between relevant documents found by the system and the number of
	 * returned documents.
	 *
	 * @param queryResults  Array of ObjScore representing query results.
	 * @param relevanceData Map of document IDs to relevance scores.
	 * @param k             The value of k for precision at k calculation.
	 * @return Precision at k.
	 */
	public float precisionAtK(ObjScore[] queryResults, Map<Integer, Integer> relevanceData, int k) {
		if (queryResults.length == 0)
			return 0;

		// System.out.println("Sto calcolando la precision at " + k);
		int relevant = 0;
		for (int i = 1; i <= Math.min(k, queryResults.length); i++)
			if (relevanceData.getOrDefault(queryResults[i - 1].getPayload(), 0) > 0)
				relevant++;

		// System.out.println("Sono nel precisionat " + k + " e di rilevanti ne ho
		// trovati: " + relevant);
		// System.out.println("Quindi il calcolo del precisionatk mi viene: " + (float)
		// relevant / Math.min(k, relevanceData.size()));

		return (float) relevant / Math.min(k, relevanceData.size());
	}

	/**
	 * Calculate average precision for a list of query results. Average precision is
	 * the average of precision at different values of k.
	 *
	 * @param queryResults  Array of ObjScore representing query results.
	 * @param relevanceData Map of document IDs to relevance scores.
	 * @return Average precision.
	 */
	public float averagePrecision(ObjScore[] queryResults, Map<Integer, Integer> relevanceData) {
		if (queryResults.length == 0)
			return 0;

		int kRB = queryResults.length;
		// System.out.println("Sono nell'average precision, la krb viene: " + kRB);
		float totalSum = 0;

		for (int i = 1; i <= kRB; i++)
			if (relevanceData.getOrDefault(queryResults[i - 1].getPayload(), 0) > 0) {
				// System.out.println("Sono nell'averageprecision e ho trovato che questo è
				// rilevante: " + i);
				totalSum += precisionAtK(queryResults, relevanceData, i);
			}

		return totalSum / kRB;
	}

	/**
	 * Calculate recall at k for a list of query results. The recall at k is the
	 * ratio between relevant documents found by the system and the total relevant
	 * documents for that query.
	 *
	 * @param queryResults  Array of ObjScore representing query results.
	 * @param relevanceData Map of document IDs to relevance scores.
	 * @param k             The value of k for recall at k calculation.
	 * @return Recall at k.
	 */
	public float recallAtK(ObjScore[] queryResults, Map<Integer, Integer> relevanceData, int k) {
		if (queryResults.length == 0)
			return 0;

		int totalRelevant = (int) relevanceData.values().stream().filter(score -> score > 0).count();

		if (totalRelevant == 0)
			return 0;

		// System.out.println("Nel recall quelle totali rilevanti sono: " +
		// totalRelevant);

		k = Math.min(k, queryResults.length);

		long relevantInTopK = Arrays.stream(queryResults).limit(k)
				.filter(entry -> relevanceData.getOrDefault(entry.getPayload(), 0) > 0).count();
		// System.out.println("Quelle rilevanti che ho trovato io sono : "+
		// relevantInTopK);

		return (float) relevantInTopK / totalRelevant;
	}

	/**
	 * Calculate discounted cumulative gain (DCG) for a list of query results. DCG
	 * takes into account both the relevance and the position of each retrieved
	 * document in the ranked list. The idea is that highly relevant documents
	 * should be placed higher in the list, and the gain (relevance) diminishes as
	 * you move down the list.
	 *
	 * @param b             The base value for logarithm in DCG calculation.
	 * @param k             The value of k for DCG calculation.
	 * @param queryResults  Array of ObjScore representing query results.
	 * @param relevanceData Map of document IDs to relevance scores.
	 * @return Discounted cumulative gain.
	 */
	public double discountedCumulativeGain(int b, int k, ObjScore[] queryResults, Map<Integer, Integer> relevanceData) {
		double DCG = 0;

		for (int i = 1; i <= Math.min(k, queryResults.length); i++) {
			// System.out.println("Sono nel DCG, relativo al document: " + queryResults[i -
			// 1].getPayload() + " ho rilevanza " +
			// relevanceData.getOrDefault(queryResults[i - 1].getPayload(), 0));
			double gain = relevanceData.getOrDefault(queryResults[i - 1].getPayload(), 0)
					/ Math.max(1, (Math.log(k) / Math.log(b)));
			DCG += gain;
		}

		return DCG;
	}

	/**
	 * Compute the standard deviation of elapsed times for query processing.
	 *
	 * @param elapsTimeArray List of elapsed times for query processing.
	 * @param average        Average elapsed time.
	 * @param numQueries     The total number of queries.
	 * @return The standard deviation.
	 */
	public float computeStandardDeviation(List<Float> elapsTimeArray, float average, int numQueries) {
		float stdDev = 0;
		for (float recording : elapsTimeArray)
			stdDev += Math.pow(recording - average, 2);

		return (float) Math.sqrt(stdDev / numQueries);
	}

	/**
	 * Evaluate the retrieval system's performance for a set of queries and
	 * relevance data. Outputs metrics such as discounted cumulative gain, recall at
	 * k, average precision, average time, and standard deviation.
	 *
	 * @param queries         Map of query IDs to query texts.
	 * @param relevance       Map of query IDs to a map of document IDs and
	 *                        relevance scores.
	 * @param scoringFunction The scoring function used for query processing.
	 * @param algorithm       The retrieval algorithm used.
	 * @param isConjunctive   Flag indicating if the query processing is
	 *                        conjunctive.
	 * @throws IOException If an I/O error occurs.
	 */
	public void evaluateSystem(Map<Integer, String> queries, Map<Integer, Map<Integer, Integer>> relevance,
			String scoringFunction, String algorithm, boolean isConjunctive) throws IOException {
		float averageTime = 0;
		float map = 0;
		int numQueries = queries.size();
		List<Float> elapsTimeArray = new ArrayList<>();

		for (Map.Entry<Integer, String> entry : queries.entrySet()) {
			int queryIdToCheck = entry.getKey();
			String queryText = entry.getValue();

			Map<Integer, Integer> docIdScorePairs = relevance.get(queryIdToCheck);
			if (docIdScorePairs == null || docIdScorePairs.isEmpty())
				continue;

			long startTime = System.currentTimeMillis();
			List<ObjScore> result = queryProcesser.processQuery(queryText, scoringFunction, algorithm, isConjunctive);
			long elapsedTime = System.currentTimeMillis() - startTime;
			elapsTimeArray.add((float) elapsedTime / 1000);
			averageTime += (float) elapsedTime / 1000;

			ObjScore[] resultArray = result.toArray(new ObjScore[0]);

			double dcg = discountedCumulativeGain(10, 10, resultArray, docIdScorePairs);
			float recallAtK = recallAtK(resultArray, docIdScorePairs, 10);
			float ap = averagePrecision(resultArray, docIdScorePairs);
			map += ap;

			System.out.println("Query ID: " + queryIdToCheck);
			System.out.println("Discounted Cumulative Gain: " + dcg);
			System.out.println("Recall at K: " + recallAtK);
			System.out.println("Average Precision: " + ap);
			// System.out.println("Elapsed Time for Query: " + elapsedTime / 1000 + "
			// seconds\n");
		}

		System.out.println("Total Average Time: " + averageTime / numQueries);
		System.out
				.println("Standard Deviation is: " + computeStandardDeviation(elapsTimeArray, averageTime, numQueries));
		System.out.println("Mean Average Precision: " + map / queries.size());
	}
}