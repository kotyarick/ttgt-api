use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct Schedule {
	pub weeks: Vec<Week>,
}

#[derive(Debug, Serialize)]
pub struct Week {
	pub days: Vec<Day>,
}

#[derive(Debug, Serialize)]
pub struct Day {
	pub lessons: Vec<Option<Lesson>>,
}

#[derive(Debug, Serialize)]
pub struct Subgroup {
	pub room: String,
	pub teacher: String,
}

impl Subgroup {
	pub fn from(thing: Vec<&str>) -> Self {
		Subgroup {
			room: thing[4].to_string(),
			teacher: format!("{} {}", thing[2], thing[3]),
		}
	}
}

#[derive(Debug, Serialize)]
pub enum Lesson {
	#[serde(rename = "commonLesson")]
	CommonLesson {
		teacher: String,
		group: String,
		room: String,
		name: String,
	},
	#[serde(rename = "subgroupedLesson")]
	SubgroupedLesson {
		name: String,
		subgroups: Vec<Subgroup>,
	},
}
