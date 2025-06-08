
import java.util.List;

public class PersonController {
    private PersonService personService;
    
    public PersonController(PersonService personService) {
        this.personService = personService;
    }
    
    public String createPerson(int id, String name, String email, String phone) {
        NewPerson person = new NewPerson(id, name);
        person.setEmail(email);
        person.setPhone(phone);
        
        personService.save(person);
        return "Person created successfully";
    }
    
    public NewPerson getPerson(int id) {
        return personService.findById(id);
    }
    
    public List<NewPerson> getAllPersons() {
        return personService.findAll();
    }
    
    public String updatePerson(NewPerson person) {
        NewPerson updated = personService.update(person);
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