//! EV-04 / LL-008: round-trip a synthetic workbook, optionally changing one existing cell.
#![forbid(unsafe_code)]

use std::path::PathBuf;

#[derive(Debug, thiserror::Error)]
enum SpikeError {
    #[error("usage: spike-xlsx <input.xlsx> <output.xlsx> <roundtrip|edit|preserving-edit>")]
    Usage,
    #[error("fixture has no Invoices sheet")]
    MissingSheet,
    #[error("output already exists: {0}")]
    OutputExists(PathBuf),
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 3 || (args[2] != "roundtrip" && args[2] != "edit" && args[2] != "preserving-edit") {
        return Err(SpikeError::Usage.into());
    }
    let input = PathBuf::from(&args[0]);
    let output = PathBuf::from(&args[1]);
    if output.exists() {
        return Err(SpikeError::OutputExists(output).into());
    }
    let started = std::time::Instant::now();
    if args[2] == "preserving-edit" {
        preserve_package(&input, &output)?;
        println!(
            "MEASURE roundtrip_ms={:.2}",
            started.elapsed().as_secs_f64() * 1000.0
        );
        return Ok(());
    }
    let mut book = umya_spreadsheet::reader::xlsx::read(&input)?;
    if args[2] == "edit" {
        book.sheet_by_name_mut("Invoices")
            .map_err(|_| SpikeError::MissingSheet)?
            .cell_mut("H2")
            .set_value_string("spike-updated.pdf");
    }
    umya_spreadsheet::writer::xlsx::write(&book, &output)?;
    println!(
        "MEASURE roundtrip_ms={:.2}",
        started.elapsed().as_secs_f64() * 1000.0
    );
    Ok(())
}

/// A narrow experiment, not an adapter: patch ONLY fixture H2 in sheet1; copy all other parts.
/// Production needs a package allowlist, quotas, authorized handles, mappings and write safety.
fn preserve_package(
    input: &std::path::Path,
    output: &std::path::Path,
) -> Result<(), Box<dyn std::error::Error>> {
    use quick_xml::events::{BytesStart, BytesText, Event};
    use std::io::{Read, Write};
    let mut source = zip::ZipArchive::new(std::fs::File::open(input)?)?;
    let file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)?;
    let mut target = zip::ZipWriter::new(file);
    let mut changed = 0;
    for index in 0..source.len() {
        let mut part = source.by_index(index)?;
        let mut data = Vec::new();
        part.read_to_end(&mut data)?;
        if part.name() == "xl/worksheets/sheet1.xml" {
            let mut reader = quick_xml::Reader::from_reader(data.as_slice());
            let mut writer = quick_xml::Writer::new(Vec::new());
            loop {
                let event = reader.read_event()?;
                if let Event::Start(ref element) = event {
                    let attributes = element.attributes().collect::<Result<Vec<_>, _>>()?;
                    if element.name().as_ref() == b"c"
                        && attributes
                            .iter()
                            .any(|a| a.key.as_ref() == b"r" && a.value.as_ref() == b"H2")
                    {
                        let mut cell = BytesStart::new("c");
                        for attribute in attributes.iter().filter(|a| a.key.as_ref() != b"t") {
                            cell.push_attribute((attribute.key.as_ref(), attribute.value.as_ref()));
                        }
                        cell.push_attribute(("t", "inlineStr"));
                        writer.write_event(Event::Start(cell))?;
                        reader.read_to_end(element.name())?;
                        writer.write_event(Event::Start(BytesStart::new("is")))?;
                        writer.write_event(Event::Start(BytesStart::new("t")))?;
                        writer.write_event(Event::Text(BytesText::new("spike-updated.pdf")))?;
                        writer.write_event(Event::End(quick_xml::events::BytesEnd::new("t")))?;
                        writer.write_event(Event::End(quick_xml::events::BytesEnd::new("is")))?;
                        writer.write_event(Event::End(quick_xml::events::BytesEnd::new("c")))?;
                        changed += 1;
                        continue;
                    }
                }
                if matches!(event, Event::Eof) {
                    break;
                }
                writer.write_event(event)?;
            }
            data = writer.into_inner();
        }
        target.start_file(
            part.name(),
            zip::write::SimpleFileOptions::default().compression_method(zip::CompressionMethod::Stored),
        )?;
        target.write_all(&data)?;
    }
    target.finish()?;
    if changed != 1 {
        return Err(SpikeError::MissingSheet.into());
    }
    Ok(())
}
