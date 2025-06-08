public  class  PersonIdentity {
	
    private int id;

	
    private String name;

	
    
    public String getFormattedIdentity() {
        return "ID: " + id + ", Name: " + name;
    }

	

    public PersonIdentity(int id, String name) {
        this.id = id;
        this.name = name;
    }

	

    public int getId() {
        return id;
    }

	

    public void setId(int id) {
        this.id = id;
    }

	

    public String getName() {
        return name;
    }

	

    public void setName(String name) {
        this.name = name;
    }


}
