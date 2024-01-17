package Test;

import org.junit.jupiter.api.Test;

import it.unipi.mircv.SearchEngine.utilities.TextProcessor;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;

class TextProcessorTest {
    private final String stopWordsFilePath = "D:\\QueryProcessing\\SearchEngine\\english_stop_words.txt";

    private static final List<String> TEST_SENTENCES = Arrays.asList(
            "This is a sentence with multiple spaces  and punctuation!",
            "https://en.wikipedia.org/wiki/List_of_Unicode_characters Brooklyn",
            "The first websiteâThe Manhattan Project:",
            "Each of these types of communitiesâ <html> zones </html>",
            "There are special characters like @, #, $, %, and ^ in this sentence.",
            "",
            "      .................   !!!!!! @#&                    ",
            " !%£&/  ($£(/  £()",
            "The $sun is shining! brightly                  ..... in the sky&&."
    );

    private static final List<String> EXPECTED_SENTENCES = Arrays.asList(
            "sentenc multipl space punctuat",
            "brooklyn",
            "first websit manhattan project",
            "type communiti zone",
            "special charact sentenc",
            "",
            "",
            "",
            "sun shine bright sky"
    );

    @Test
    void testTextProcessingWithoutStemmingAndStopWords() {
        TextProcessor textProcessor = new TextProcessor(true, stopWordsFilePath);

        for (int i = 0; i < TEST_SENTENCES.size(); i++) {
            String inputSentence = TEST_SENTENCES.get(i);
            String expectedProcessedSentence = EXPECTED_SENTENCES.get(i);

            String processedTokens = textProcessor.processText(inputSentence);
            String processedSentence = String.join(" ", processedTokens);

            assertEquals(expectedProcessedSentence, processedSentence,
                    "Processed sentence should match expected sentence for input: " + inputSentence);
        }
    }

    @Test
    void testStemText() {
        TextProcessor textProcessor = new TextProcessor(true, stopWordsFilePath);

        List<String> tokens = Arrays.asList("running", "jumps", "played");
        List<String> stemmedTokens = textProcessor.stemText(tokens);

        List<String> expectedStemmedTokens = Arrays.asList("run", "jump", "play");
        assertEquals(expectedStemmedTokens, stemmedTokens, "Stemmed tokens should match expected stemmed tokens");
    }

    @Test
    void testRemoveStopWords() {
        TextProcessor textProcessor = new TextProcessor(true, stopWordsFilePath);

        List<String> tokens = Arrays.asList("this", "is", "a", "sample", "text", "with", "stopwords");
        List<String> filteredTokens = textProcessor.removeStopWords(tokens);

        List<String> expectedFilteredTokens = Arrays.asList("sample", "text", "stopwords");
        assertEquals(expectedFilteredTokens, filteredTokens, "Filtered tokens should match expected filtered tokens");
    }

    @Test
    void testCleanText() {
        TextProcessor textProcessor = new TextProcessor(true, stopWordsFilePath);

        String inputText = "This is a sample text with <html> tags, #biden, @usernames, and http://wikipedia.";
        String cleanedText = textProcessor.cleanText(inputText);

        String expectedCleanedText = "this is a sample text with tags usernames and";
        assertEquals(expectedCleanedText, cleanedText, "Cleaned text should match expected cleaned text");
    }

    @Test
    void testTokenizeText() {
        TextProcessor textProcessor = new TextProcessor(true, stopWordsFilePath);

        String inputText = "Tokenizing this text into words.";
        List<String> tokens = textProcessor.tokenizeText(inputText);

        List<String> expectedTokens = Arrays.asList("Tokenizing", "this", "text", "into", "words.");
        assertEquals(expectedTokens, tokens, "Tokenized text should match expected tokens");
    }
}
