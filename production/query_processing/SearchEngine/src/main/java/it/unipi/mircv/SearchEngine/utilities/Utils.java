package it.unipi.mircv.SearchEngine.utilities;

import java.io.File;
import java.io.IOException;

public class Utils {

    public static File createFileIfNotExists(String filePath) throws IOException {
        File file = new File(filePath);

        if (!file.exists()) {
            if (file.createNewFile()) {
                System.out.println("File created: " + file.getAbsolutePath());
            } else {
                throw new IOException("Failed to create the file: " + file.getAbsolutePath());
            }
        }

        return file;
    }

}
