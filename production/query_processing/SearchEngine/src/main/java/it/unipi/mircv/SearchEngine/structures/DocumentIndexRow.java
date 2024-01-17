package it.unipi.mircv.SearchEngine.structures;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;


/**
 * Todo
 * 
 * @author Gabriele
 *
 */
public class DocumentIndexRow {

    public static final int SIZE_DOC_INDEX_ROW = 36; // Dimensione in byte della struct

    //private long docId;
    private String docNo;
    private int documentLength;

    public DocumentIndexRow(long docId, String docNo, String text) {
        if (!(docNo instanceof String) || !(text instanceof String)) {
            throw new IllegalArgumentException("docId must be a long, docNo must be a String, and text must be a String.");
        }

        //this.docId = docId;
        this.docNo = String.format("%-30s", docNo);
        this.documentLength = countWords(text);
    }

    public DocumentIndexRow(){
        //this.docId = 0;
        this.docNo =  "";
        this.documentLength = 1;
    }

    private int countWords(String text) {
        if (!(text instanceof String)) {
            throw new IllegalArgumentException("text must be a String.");
        }

        if (text.trim().isEmpty()) {
            return 0;
        }

        return text.split("\\s+").length;
    }

    public String toString() {
        return docNo.trim() + " " + documentLength;
    }

    public long readDocIndexRowOnDisk(RandomAccessFile file,long offset) throws IOException {
        
        file.seek(offset);

        byte[] binaryData = new byte[SIZE_DOC_INDEX_ROW];
        file.readFully(binaryData);

        ByteBuffer buffer = ByteBuffer.wrap(binaryData).order(ByteOrder.LITTLE_ENDIAN);
        
        //this.docId=buffer.getLong();
        this.docNo=new String(binaryData, 0, 30);
       
        buffer.position(32);
        
        this.documentLength=buffer.getInt();

        return offset + SIZE_DOC_INDEX_ROW;
    }

    
    /** Next all the getter methods that expose the private variables and allows to handle them in a "safety way".*/
    
    public int getDocumentLength() {
        return documentLength;
    }


    public String getDocNo() {
        return docNo;
    }


}
