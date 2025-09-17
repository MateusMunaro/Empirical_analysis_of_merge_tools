public class AddressBook {
    private Map<Integer, String> userAddresses;
    
    public void addUserAddress(int userId, String address) {
        userAddresses.put(userId, address);
    }
    
    public String getUserAddress(int userId) {
        return userAddresses.get(userId);
    }
}