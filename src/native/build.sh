cargo build -r --target x86_64-unknown-linux-gnu && \
cargo build -r --target x86_64-pc-windows-gnu

mv target/x86_64-unknown-linux-gnu/release/libbackend.so .
mv target/x86_64-pc-windows-gnu/release/backend.dll .

strip libbackend.so backend.dll
