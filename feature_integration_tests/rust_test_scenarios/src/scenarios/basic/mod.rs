use crate::internals::scenario::{ScenarioGroup, ScenarioGroupImpl};

pub mod basic;
pub struct BasicScenarioGroup {
    group: ScenarioGroupImpl,
}

impl BasicScenarioGroup {
    pub fn new() -> Self {
        BasicScenarioGroup {
            group: ScenarioGroupImpl::new("basic"),
        }
    }
}

impl ScenarioGroup for BasicScenarioGroup {
    fn get_group_impl(&mut self) -> &mut ScenarioGroupImpl {
        &mut self.group
    }

    fn init(&mut self) -> () {
        self.group.add_scenario(Box::new(basic::CycleCounter));
    }
}
