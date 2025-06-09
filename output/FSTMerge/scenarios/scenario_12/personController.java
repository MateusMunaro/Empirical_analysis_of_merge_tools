import java.util.List; 

public   class  PersonController {
	
    private PersonService personService  ;

	
    
    public PersonController  (PersonService personService) {
        this.personService = personService;
    
        this.personService = personService;
    
        this.personService = personService;
    }

	
    
    public String createPerson  (int id, String name, String email, String phone) {
        Person person = initializePerson(id, name);
        fillPersonDetails(person, email, phone);
        persistPerson(person);
        return "Person created successfully";
    }

	
    
    public Person getPerson  (int id) {
        validateId(id);
        return fetchPerson(id);
    }

	
    
    public List<Person> getAllPersons  () {
        return personService.findAll();
    }

	
    
    public String updatePerson  (Person person) {
        validatePerson(person);
        Person updated = performUpdate(person);
        return generateUpdateMessage(updated);
    }

	
    
    public String deletePerson  (int id) {
        validateId(id);
        if (checkPersonExists(id)) {
            performDelete(id);
            return "Person deleted successfully";
        }
        return "Person not found";
    }

	
    
    private Person initializePerson  (int id, String name) {
        return new Person(id, name);
    }

	
    
    private void fillPersonDetails  (Person person, String email, String phone) {
        person.setEmail(email);
        person.setPhone(phone);
    }

	
    
    private void persistPerson  (Person person) {
        personService.save(person);
    }

	
    
    private void validateId  (int id) {
        if (id <= 0) {
            throw new IllegalArgumentException("ID must be greater than zero");
        }
    }

	
    
    private Person fetchPerson  (int id) {
        return personService.findById(id);
    }

	
    
    private void validatePerson  (Person person) {
        if (person == null || person.getId() <= 0) {
            throw new IllegalArgumentException("Invalid person data");
        }
    }

	
    
    private Person performUpdate  (Person person) {
        return personService.update(person);
    }

	
    
    private String generateUpdateMessage  (Person updated) {
        if (updated != null) {
            return "Person updated successfully";
        }
        return "Person not found";
    }

	
    
    private boolean checkPersonExists  (int id) {
        return personService.exists(id);
    }

	
    
    private void performDelete  (int id) {
        personService.delete(id);
    }


}
