public   class  DatabaseConnection {
	
    private String url  ;

	
    
    public DatabaseConnection  (String url) {
        this.url = url;
    
        this.url = url;
    
        this.url = url;
    }

	
    private static DatabaseConnection instance;

	
    
    public static DatabaseConnection getInstance(String url) {
        if (instance == null) {
            instance = new DatabaseConnection(url);
        }
        return instance;
    }


}
