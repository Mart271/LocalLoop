//! SPIKE (LL-011): helpers shared by the spike worker and supervisor. Throwaway code.
//!
//! Frames are a 4-byte big-endian length followed by UTF-8 text, the same framing the document
//! worker protocol uses (component-design §10.1), with plain text payloads to keep the spike small.

#![forbid(unsafe_code)]

use std::io::{self, Read, Write};

pub const MAX_FRAME: u32 = 1024 * 1024;

pub fn write_frame(out: &mut impl Write, text: &str) -> io::Result<()> {
    let len = u32::try_from(text.len()).map_err(|_| io::Error::other("frame too large"))?;
    if len > MAX_FRAME {
        return Err(io::Error::other("frame exceeds limit"));
    }
    out.write_all(&len.to_be_bytes())?;
    out.write_all(text.as_bytes())?;
    out.flush()
}

/// Reads one frame. `Ok(None)` means the other side closed the pipe (end of file).
pub fn read_frame(input: &mut impl Read) -> io::Result<Option<String>> {
    let mut len = [0u8; 4];
    if input.read(&mut len[..1])? == 0 {
        return Ok(None);
    }
    input.read_exact(&mut len[1..])?;
    let len = u32::from_be_bytes(len);
    if len > MAX_FRAME {
        return Err(io::Error::other("frame exceeds limit"));
    }
    let mut buf = vec![0u8; len as usize];
    input.read_exact(&mut buf)?;
    String::from_utf8(buf).map(Some).map_err(io::Error::other)
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    use sha2::{Digest, Sha256};
    Sha256::digest(bytes).iter().map(|b| format!("{b:02x}")).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn framing_rejects_truncation_oversize_and_invalid_utf8() {
        assert!(read_frame(&mut &[][..]).unwrap().is_none());
        assert!(read_frame(&mut &[0, 0][..]).is_err());
        assert!(read_frame(&mut &((MAX_FRAME + 1).to_be_bytes())[..]).is_err());
        assert!(read_frame(&mut &[0, 0, 0, 1, 255][..]).is_err());
        let mut output = Vec::new();
        assert!(write_frame(&mut output, &"x".repeat(MAX_FRAME as usize + 1)).is_err());
        assert!(output.is_empty());
        write_frame(&mut output, "hello").unwrap();
        assert_eq!(
            read_frame(&mut output.as_slice()).unwrap(),
            Some("hello".to_owned())
        );
    }
}
