public class DatabaseConnection {
    private static DatabaseConnection instance;
    private String url;
    
    private DatabaseConnection(String url) {
        this.url = url;
    }
    
    public static DatabaseConnection getInstance(String url) {
        if (instance == null) {
            instance = new DatabaseConnection(url);
        }
        return instance;
    }
}