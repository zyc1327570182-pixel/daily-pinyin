#!/usr/bin/env bash
# Rebuild the bundled native libraries from the exact source archives.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "$0")/.." && pwd)"
build_dir="${1:-$project_dir/build/native}"
mkdir -p "$build_dir/src" "$build_dir/prefix"
for component in librime lua octagram frontend predict; do
  mkdir -p "$build_dir/src/$component"
  tar -xzf "$project_dir/sources/$component-source.tar.gz" --strip-components=1 -C "$build_dir/src/$component"
done
cp -a "$build_dir/src/lua" "$build_dir/src/librime/plugins/lua"
cp -a "$build_dir/src/octagram" "$build_dir/src/librime/plugins/octagram"
cp -a "$build_dir/src/predict" "$build_dir/src/librime/plugins/predict"
patch -d "$build_dir/src/librime/plugins/predict" -p1 < "$project_dir/sources/predict-user-experience.patch"
patch -d "$build_dir/src/frontend" -p1 < "$project_dir/sources/frontend-user-data.patch"
cmake -S "$build_dir/src/librime" -B "$build_dir/rime" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$build_dir/prefix" \
  -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_TEST=OFF -DBUILD_DATA=OFF \
  -DBUILD_SAMPLE=OFF -DBUILD_TOOLS=ON -DBUILD_MERGED_PLUGINS=ON \
  "-DCMAKE_CXX_FLAGS=-ffile-prefix-map=$build_dir/src=."
cmake --build "$build_dir/rime" -j"${JOBS:-4}"
cmake --install "$build_dir/rime"
PKG_CONFIG_PATH="$build_dir/prefix/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}" \
cmake -S "$build_dir/src/frontend" -B "$build_dir/frontend" \
  -DCMAKE_BUILD_TYPE=Release -DRIME_DATA_DIR=/usr/share/rime-data \
  "-DCMAKE_CXX_FLAGS=-ffile-prefix-map=$build_dir/src=."
cmake --build "$build_dir/frontend" -j"${JOBS:-4}"
mkdir -p "$project_dir/payload/runtime/lib" "$project_dir/payload/runtime/fcitx5"
cp -a "$build_dir/prefix/lib/"librime.so* "$project_dir/payload/runtime/lib/"
cp "$build_dir/frontend/src/librime.so" "$project_dir/payload/runtime/fcitx5/librime.so"
patchelf --set-rpath '$ORIGIN' "$project_dir/payload/runtime/lib/librime.so.1.17.0"
patchelf --set-rpath '$ORIGIN/../lib' "$project_dir/payload/runtime/fcitx5/librime.so"
printf '%s\n' 'Native build complete. See docs/BUILD.md for runtime dependencies and dictionaries.'
