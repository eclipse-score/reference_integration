use crate::internals::scenario::{ScenarioGroup, ScenarioGroupImpl};
use basic::BasicScenarioGroup;

pub mod basic;

pub struct RootScenarioGroup {
    group: ScenarioGroupImpl,
}

impl RootScenarioGroup {
    pub fn new() -> Self {
        RootScenarioGroup {
            group: ScenarioGroupImpl::new("root"),
        }
    }
}

impl ScenarioGroup for RootScenarioGroup {
    fn get_group_impl(&mut self) -> &mut ScenarioGroupImpl {
        &mut self.group
    }

    fn init(&mut self) -> () {
        self.group.add_group(Box::new(BasicScenarioGroup::new()));
    }
}
