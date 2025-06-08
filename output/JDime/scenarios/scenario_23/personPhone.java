public class PersonPhone {
    private String phone;
    
    public String getFormattedPhone() {
        return "Phone: " + phone;
    }

    public PersonPhone(String phone) {
        this.phone = phone;
    }

    public String getPhone() {
        return phone;
    }
    
    public void setPhone(String phone) {
        this.phone = phone;
    }
}
