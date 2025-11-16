use serde::Serialize;

#[derive(Debug)]
pub enum ItemType {
    Teacher,
    Group,
}

#[derive(Serialize)]
pub struct Items {
    pub teachers: Vec<String>,
    pub groups: Vec<String>,
}
