public  class  User {
	
    private int userId;

	 
    private String name;

	 
    private String mail;

	 

    public User(int userId, String name, String mail) {
        this.userId = userId;
        this.name = name;
        this.mail = mail;
    }

	

    public int getUserId() {
        return userId;
    }

	

    public void setUserId(int userId) {
        this.userId = userId;
    }

	

    public String getName() {
        return name;
    }

	

    public void setName(String name) {
        this.name = name;
    }

	

    public String getMail() {
        return mail;
    }

	

    public void setMail(String mail) {
        this.mail = mail;
    }


}
