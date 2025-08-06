use super::scenario::ScenarioGroup;

pub struct TestContext {
    root_group: Box<dyn ScenarioGroup>,
}

impl TestContext {
    pub fn new(root_group: Box<dyn ScenarioGroup>) -> Self {
        TestContext { root_group: root_group }
    }

    pub fn run_scenario(&mut self, name: &str, input: Option<String>) -> () {
        let scenario = self.root_group.find_scenario(name);
        match scenario {
            Some(scenario) => scenario.run(input).expect("Run failed"),
            None => panic!("Scenario {} not found", name),
        };
    }
    pub fn list_scenarios(&mut self) -> () {
        let scenarios = self.root_group.list_scenarios(None);
        for scenario in scenarios {
            println!("{}", scenario);
        }
    }
}
