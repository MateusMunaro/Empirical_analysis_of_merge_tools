public  class  PersonEmail {
	
    private String email;

	
    
    public String getFormattedEmail() {
        return "Email: " + email;
    }

	

    public PersonEmail(String email) {
        this.email = email;
    }

	

    public String getEmail() {
        return email;
    }

	
    
    public void setEmail(String email) {
        this.email = email;
    }


}
