public class User {
    private int id;
    private String name;
    
    public void saveUser() {
        // logic to save user
        System.out.println("User saved: " + name);
    }
    
    public String getFormattedInfo() {
        return "User: " + name + " (ID: " + id + ")";
    }
}

