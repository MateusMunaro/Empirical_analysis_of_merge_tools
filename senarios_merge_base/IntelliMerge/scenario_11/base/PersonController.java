import java.util.List;

public class PersonController {
    private PersonService personService;
    
    public PersonController(PersonService personService) {
        this.personService = personService;
    }
    
    public String createPerson(int id, String name, String email, String phone) {
        Person person = new Person(id, name);
        person.setEmail(email);
        person.setPhone(phone);
        
        personService.save(person);
        return "Person created successfully";
    }
    
    public Person getPerson(int id) {
        return personService.findById(id);
    }
    
    public List<Person> getAllPersons() {
        return personService.findAll();
    }
    
    public String updatePerson(Person person) {
        Person updated = personService.update(person);
        if (updated != null) {
            return "Person updated successfully";
        }
        return "Person not found";
    }
    
    public String deletePerson(int id) {
        if (personService.exists(id)) {
            personService.delete(id);
            return "Person deleted successfully";
        }
        return "Person not found";
    }
}