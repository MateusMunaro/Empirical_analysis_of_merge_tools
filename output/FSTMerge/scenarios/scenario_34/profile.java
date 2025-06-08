public  class  Profile {
	
    private int userId;

	
    private String userName;

	
    private String location;

	
    
    public void saveProfile() {
        // lógica para salvar perfil que inclui usuário
    }

	
    
    public String getUserInfo() {
        return "User: " + userName + " (ID: " + userId + ")";
    }

	
    
    public String getLocationInfo() {
        return "Location: " + location;
    }


}
