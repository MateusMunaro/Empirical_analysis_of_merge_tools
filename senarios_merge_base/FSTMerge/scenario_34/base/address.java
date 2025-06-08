public class Address {
    private String street;
    private String city;
    
    public String getFullAddress() {
        return street + ", " + city;
    }
}