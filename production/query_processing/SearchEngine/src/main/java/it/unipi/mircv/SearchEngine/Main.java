package it.unipi.mircv.SearchEngine;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;
import java.util.Scanner;

import it.unipi.mircv.SearchEngine.handlers.QueryProcesser;
import it.unipi.mircv.SearchEngine.utilities.Scoring.ObjScore;

public class Main {
	
	
	public static void main(String[] args) {
		
		Properties properties = new Properties();
		
		Scanner scanner = new Scanner(System.in);
		
		String fileProperties = "config.properties";
		
		String pathStopWords= "";
		String pathDocIndex= "";
		String pathLexicon = "";
		String pathDocIds = "";
		String pathFreqs = "";
		String pathBlocks ="";
		String pathCollStat = "";
		
		boolean COMPRESSION_MODE=false;
		boolean USE_STEMMING_AND_STOPWORD_REMOVAL=false;
		
		boolean CONJUNCTIVE_MODE=false;
		boolean USE_CACHE=false;
		int KTOPRESULTS=10;
		String FUNCTION="tfidf";
		String ALGORITHM="daat";
		
		
		FileInputStream inputConfig = null;
		try {
			// Load properties from config.properties file.
			
			inputConfig = new FileInputStream(fileProperties);
			properties.load(inputConfig);
	        
			pathStopWords= properties.getProperty("pathStopWords");
			pathDocIndex = properties.getProperty("pathDocIndex");
			
			pathLexicon = properties.getProperty("pathLexicon");
			pathDocIds = properties.getProperty("pathDocIds");
			pathFreqs = properties.getProperty("pathFreqs");
			pathBlocks = properties.getProperty("pathBlocks");
			
			pathCollStat = properties.getProperty("pathCollStat");
			
			COMPRESSION_MODE=properties.getProperty("COMPRESSION_MODE").equals("true")?true:false;
			USE_STEMMING_AND_STOPWORD_REMOVAL=properties.getProperty("USE_STEMMING_AND_STOPWORD_REMOVAL").equals("true")?true:false; 
			
			inputConfig.close();
		
		} catch (Exception e) {
			
			e.printStackTrace();
			System.err.println("Some of the properties are not configured correctly. The program will be quit..");
			scanner.close();
			return;
		}
		
        

		QueryProcesser queryProcesser=null;
		try {
			System.out.println("\n\n");
			System.out.println("*************************************");
			System.out.println("*                                   *");
			System.out.println("*         Quering execution         *");
			System.out.println("*                                   *");
			System.out.println("*************************************");
			System.out.println("\n");
			
			System.out.println("Settings: ");
		
			while (true) {
				System.out.println("Function to use (tfidf/bm25): (default 'tfidf') ");
				String conj = scanner.nextLine();
				
				if (conj.trim().equals("")) {
					break;
				}
				if (conj.toLowerCase().equals("bm25")){
					FUNCTION="bm25";
					break;
				}
				if (conj.toLowerCase().equals("tfidf")){
					FUNCTION="tfidf";
					break;
				}
			}
			
			while (true) {
				System.out.println("Algorithm to use (daat/maxScore): (default 'daat') ");
				String conj = scanner.nextLine();
				
				if (conj.trim().equals("")) {
					break;
				}
				if (conj.toLowerCase().equals("daat")){
					ALGORITHM="daat";
					break;
				}
				if (conj.toLowerCase().equals("maxscore")){
					ALGORITHM="maxScore";
					break;
				}
			}
			

			while (true) {
				System.out.println("Use CONJUNCTIVE search (y/n): (default 'n') ");
				String conj = scanner.nextLine();
				
				if (conj.trim().equals("")) {
					break;
				}
				if (conj.toLowerCase().equals("y")){
					CONJUNCTIVE_MODE=true;
					break;
				}
				if (conj.toLowerCase().equals("n")){
					CONJUNCTIVE_MODE=false;
					break;
				}
			}
			
			while (true) {
				System.out.println("Use CACHE (y/n): (default 'n') ");
				String ris = scanner.nextLine();
				
				if (ris.trim().equals("")) {
					break;
				}
				if (ris.toLowerCase().equals("y")){
					USE_CACHE=true;
					break;
				}
				if (ris.toLowerCase().equals("n")){
					USE_CACHE=false;
					break;
				}
			}
			
			while (true) {
				System.out.println("Number of k-top-results: (default 10) ");
				String input = scanner.nextLine();
				
				if (input.trim().equals("")) {
					break;
				}
				
				try {
					int num=Integer.parseInt(input);
					if (num>0) {
						KTOPRESULTS=num;
						break;
					}
				}
				catch(Exception ex2) {}
			}
			
			queryProcesser= new QueryProcesser(
					pathDocIndex,
					pathLexicon,
					pathCollStat,
					pathDocIds,
					pathFreqs,
					pathBlocks,
					pathStopWords,
					USE_STEMMING_AND_STOPWORD_REMOVAL,
					COMPRESSION_MODE,
					USE_CACHE,
					KTOPRESULTS
					);
			
			System.out.println("\n\nRecap: ");
			System.out.println("Use stemming and remove stopwords : "+(USE_STEMMING_AND_STOPWORD_REMOVAL?"y":"n"));
			System.out.println("Use compression : "+(COMPRESSION_MODE?"y":"n"));
			System.out.println("CONJUNCTIVE search (y/n): "+(CONJUNCTIVE_MODE?"y":"n"));
			System.out.println("NUMBER K-TOP RESULTS: "+KTOPRESULTS+"\n");
			
			System.out.println("ALGORITHM: "+ALGORITHM);
			System.out.println("FUNCTION: "+FUNCTION+"\n");
			
			System.out.println("Path Document Index: "+pathDocIndex);
			System.out.println("Path Lexicon Index: "+pathLexicon);
			System.out.println("Path Collection Statistics : "+pathCollStat);
			System.out.println("Path StopWords  : "+pathStopWords+"\n");
			
			
			System.out.println("Path DocIds  : "+pathDocIds);
			System.out.println("Path Freq    : "+pathFreqs);
			System.out.println("Path Blocks  : "+pathBlocks);
			
			
			System.out.println("\nQuerying START");
			
			System.out.println("\n\n");
			
			while (true){
				
				System.out.println("Submit your query and press ENTER: ");
				
				String query = scanner.nextLine();
				
				long start=System.currentTimeMillis();
				
				List<ObjScore> ris = queryProcesser.processQuery(query, FUNCTION,ALGORITHM, CONJUNCTIVE_MODE);
				
				long end=System.currentTimeMillis();
				System.out.println("Query execution time: "+(end-start)+"ms");
				
				if (ris!=null && !ris.isEmpty()) {
					int i=1;
					for (Iterator<ObjScore> iterator = ris.iterator(); iterator.hasNext();) {
						ObjScore entry = (ObjScore) iterator.next();
						System.out.println((i++)+") "+entry);
					}
					System.out.println("\n");
				}else {
					System.out.println("No document found!\n");
				}
			}
			
			
		} catch (Exception e1) {
			e1.printStackTrace();
		}
		finally {
			if (queryProcesser!=null) {
				queryProcesser.closeFiles();
			}
			scanner.close();
		}
		
		
		
		
		
		
		
		
//		RandomAccessFile fileDocIndex=null;
//		RandomAccessFile fileLexicon=null;
//		
//		RandomAccessFile fileDocIds=null;
//		RandomAccessFile fileFreqs = null;
//		RandomAccessFile fileBlocks = null;
//		
//
//		try {
//			fileLexicon= new RandomAccessFile(pathLexicon, "r");
//			fileDocIds = new RandomAccessFile(pathDocIds, "r");
//			fileFreqs = new RandomAccessFile(pathFreqs, "r");
//			fileBlocks= new RandomAccessFile(pathBlocks, "r");
//			
//			fileDocIndex= new RandomAccessFile(pathDocIndex, "r");
//
//			DocumentIndexRow docIndexRow = new DocumentIndexRow(0, "0", "");
//			
//			docIndexRow.readDocIndexRowOnDisk(fileDocIndex, 18*44);
//			
//			CollectionStatistics cs= new CollectionStatistics(pathCollStat);
//			
//			//Lexicon lexicon = new Lexicon(1000, fileLexicon, cs);
//			
//			
//			DAAT daat = new DAAT(10, fileLexicon,fileDocIndex, cs, fileBlocks, fileFreqs, fileDocIds,COMPRESSION_MODE);
//			daat.resetLists();
//			List<String> stringList = new ArrayList<>();
//			stringList.add("what");
//			stringList.add("do");
//			stringList.add("you");
//			stringList.add("when");
//			stringList.add("have");
//			stringList.add("a");
//			stringList.add("nosebleed");
//			stringList.add("from");
//			stringList.add("your");
//			stringList.add("nose");
//			   
//			//stringList.add("resturant");
//			//stringList.add("dinner");
//			//what do you do when you have a nosebleed from having your nose
//			
////			stringList.add("a"); // 472327:1 472334:1 908563:1 1791331:1
////			stringList.add("best"); // 7098672:1 7921810:1 8185306:1
////			stringList.add("day");
////			stringList.add("cloud");
//			//stringList.add("comparisonsof"); // 808155:1 808156:1
//			
//
//			long start=System.currentTimeMillis();
//			List<ObjScore> ris = daat.scoreQuery("bm25", stringList, CONJUNCTIVE_MODE);
//			long end=System.currentTimeMillis();
//			System.out.println("Tempo impiegato: "+(end-start)+"\n\n");
//			
//			
//			for (Iterator<ObjScore> iterator = ris.iterator(); iterator.hasNext();) {
//				ObjScore entry = (ObjScore) iterator.next();
//				System.out.println(entry);
//			}
////		
////			System.out.println("Termine: "+lexiconRow.getTerm());
////			
////			
////			List<Long> risultati= new ArrayList<Long>();
////			List<Long> tempiEsecuzione=new ArrayList<Long>();
////					
////			
////			
////			
////			for (int i=0;i<1;i++) {
////				
////				System.out.println("Esecuzione nr:"+(i));
////				
////				PostingListHandler postingListHandler= new PostingListHandler(lexiconRow, true, fileDocIds, fileFreqs, fileBlocks);
////				//long start=System.currentTimeMillis();
////				int var=0;
////				for (Iterator<Posting> iterator = postingListHandler; iterator.hasNext();) {
////					Posting posting = (Posting) iterator.next();
////					System.out.println(posting.toString());
////					var++;
////				}
////				//long end=System.currentTimeMillis();
////				System.out.println("COUNT: "+var);
////				
////				System.out.println("Tempo impiegato solo lettura: "+postingListHandler.tempiLetturaDisco);
////				System.out.println("Tempo impiegato esecuzione: "+((end-start)-postingListHandler.tempiLetturaDisco));
////				System.out.println("Tempo impiegato: "+(end-start)+"\n\n");
////				
////				
////				
////				
////				risultati.add((end-start));
////				tempiEsecuzione.add(((end-start)-postingListHandler.tempiLetturaDisco));
////				
////			}
////			
////			
////			DoubleSummaryStatistics stats = risultati.stream().mapToDouble(Long::doubleValue).summaryStatistics();
////			
////			DoubleSummaryStatistics statsExe= tempiEsecuzione.stream().mapToDouble(Long::doubleValue).summaryStatistics();
////			
////			double media = stats.getAverage();
////			System.out.println("Media tempi su "+risultati.size()+" tentativi: "+stats.getAverage());
////			
////			System.out.println("Media tempi exe : "+statsExe.getAverage());
////			
////			
////			double varianza=0;
////			for (Iterator<Long> iterator = risultati.iterator(); iterator.hasNext();) {
////				Long tempo = (Long) iterator.next();
////				double diff=media-tempo;
////				
////				varianza+=Math.pow(diff, 2);
////			}
////			
////			
////			System.out.println("Deviazione standard: "+Math.sqrt(varianza));
////			
//			
//			
//		} catch (Exception e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}
//		
//		
//		

//		System.out.println("AAAAAAAAAAAAAAAAAA");
//		int count=0;
//		for (Iterator<Posting> iterator = reader; iterator.hasNext();) {
//			Posting posting = (Posting) iterator.next();
//			System.out.println(posting.toString());
//			count++;
//		}
//		
//		System.out.println("COUNT:"+count);		
		
		
		
		
	}
	

	
	
	
	

}
