pub mod schedule;
pub mod types;

use schedule::*;
use types::*;

use encoding::DecoderTrap;
use encoding::Encoding;
use encoding::all::WINDOWS_1251;
use scraper::{Html, Selector};
use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use zip::ZipArchive;

use std::io::Write;

trait Strip {
    fn strip(&self) -> String;
}

impl<T: AsRef<str>> Strip for T {
    fn strip(&self) -> String {
        let this = self.as_ref();
        let mut result = String::with_capacity(this.len());
        let mut words = this.split_whitespace();

        if let Some(word) = words.next() {
            result.push_str(word);

            for word in words {
                result.push(' ');
                result.push_str(word);
            }
        }

        result
    }
}

#[unsafe(no_mangle)]
pub fn parse() {
    let archive = File::open("./schedule.zip").expect("schedule.zip");
    let mut archive = ZipArchive::new(archive).expect("не валидный zip");

    let target_name_selector =
        Selector::parse(r#"font[face="Times New Roman"][size="6"][color="\#ff00ff"]"#).unwrap();
    let table = Selector::parse("table").unwrap();
    let row = Selector::parse("tr").unwrap();
    let col = Selector::parse("td").unwrap();
    //let cell = Selector::parse(r#"font[face="Arial"][size="1"]"#)?;

    let mut items = Items {
        teachers: vec![],
        groups: vec![],
    };
    let mut schedules: HashMap<String, Schedule> = HashMap::new();

    for idx in 0..archive.len() {
        let mut entry = archive.by_index(idx).unwrap();
        let name = entry.enclosed_name();
        let Some(name) = name else {
            continue;
        };
        if !name.to_string_lossy().ends_with(".html") {
            continue;
        }
        let mut html = Vec::new();
        entry.read_to_end(&mut html).unwrap();

        let html = WINDOWS_1251.decode(&html, DecoderTrap::Strict).unwrap();

        let html = Html::parse_document(&html);

        let Some(target_name) = html
            .select(&target_name_selector)
            .next()
            .and_then(|elem| elem.text().next())
            .map(|text| text.strip())
        else {
            continue;
        };
        let target_name = target_name.as_str();

        if matches!(target_name, "." | "ВАКАНСИЯ") {
            continue;
        }

        let target_type = if target_name.contains(".") {
            ItemType::Teacher
        } else {
            ItemType::Group
        };

        match target_type {
            ItemType::Teacher => items.teachers.push(target_name.to_string()),
            ItemType::Group => items.groups.push(target_name.to_string()),
        }

        let mut schedule = Schedule { weeks: vec![] };

        for table in html.select(&table) {
            let mut week = Week { days: vec![] };

            for row in table.select(&row).skip(2) {
                let mut day = Day { lessons: vec![] };

                let cells = row.select(&col);

                for cell in cells.skip(1) {
                    let mut text = cell.text().peekable();
                    let mut peek = text.peek().map(|t| t.to_string());

                    if peek.clone().is_some_and(|text| text == "\n") {
                        let _ = text.next();
                        peek = text.peek().map(|t| t.to_string());
                    }

                    peek = peek.map(|t| t.strip());

                    if peek.is_none_or(|text| matches!(text.as_str(), "" | "-" | "_" | " ")) {
                        day.lessons.push(None);
                        continue;
                    }

                    match target_type {
                        ItemType::Teacher => {
                            let group = text.next().expect("group").strip();
                            let name = text.next().expect("name").strip();
                            let room = text.next().expect("room").strip();

                            day.lessons.push(Some(Lesson::CommonLesson {
                                teacher: target_name.to_string(),
                                group,
                                room,
                                name,
                            }));
                        }
                        ItemType::Group => {
                            let name = text.next().expect("name").strip();
                            //dbg!(&name);
                            let second_line = text
                                .next()
                                .expect("second_line")
                                .split_whitespace()
                                .collect::<Vec<&str>>();
                            let lesson = match text
                                .next()
                                .map(|text| text.split_whitespace().collect::<Vec<&str>>())
                            {
                                Some(third_line) => Lesson::SubgroupedLesson {
                                    name,
                                    subgroups: vec![
                                        Subgroup::from(second_line),
                                        Subgroup::from(third_line),
                                    ],
                                },
                                None => Lesson::CommonLesson {
                                    name,
                                    group: target_name.to_string(),
                                    teacher: format!("{} {}", second_line[0], second_line[1]),
                                    room: second_line[2].to_string(),
                                },
                            };
                            day.lessons.push(Some(lesson));
                        }
                    }
                }
                week.days.push(day);
            }
            schedule.weeks.push(week);
        }

        schedules.insert(target_name.to_string(), schedule);
    }

    items.teachers.sort();
    items.groups.sort();

    let mut file = File::create("schedule.json").expect("schedule.json");
    file.write_all(serde_json::to_string(&schedules).unwrap().as_bytes())
        .expect("write schedule error");

    let mut file = File::create("items.json").expect("items.json");
    file.write_all(serde_json::to_string(&items).unwrap().as_bytes())
        .expect("write items error");
}
