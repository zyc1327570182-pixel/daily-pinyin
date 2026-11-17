#include <rime_api.h>
#include <dlfcn.h>
#include <chrono>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
  auto* api = rime_get_api();
  if (argc < 3) return 2;
  const std::string libs = argv[1], data = argv[2];
  const char* modules[] = {"default", "lua", "octagram", nullptr};
  RIME_STRUCT(RimeTraits, traits);
  traits.shared_data_dir = data.c_str();
  traits.user_data_dir = data.c_str();
  traits.app_name = "rime.dailyprobe";
  traits.modules = modules;
  traits.min_log_level = 2;
  traits.log_dir = "";
  api->setup(&traits);
  api->initialize(&traits);
  if (api->start_maintenance(True)) api->join_maintenance_thread();
  const auto session = api->create_session();
  if (!session || !api->select_schema(session, "wanxiang")) return 4;
  std::string input;
  while (std::getline(std::cin, input)) {
    api->clear_composition(session);
    api->set_option(session, "ascii_mode", False);
    const auto start = std::chrono::steady_clock::now();
    api->simulate_key_sequence(session, input.c_str());
    const auto ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now()-start).count();
    RIME_STRUCT(RimeContext, ctx);
    std::cout << input << "\t" << ms;
    if (api->get_context(session, &ctx)) {
      for (int i=0; i<ctx.menu.num_candidates && i<5; ++i)
        std::cout << "\t" << ctx.menu.candidates[i].text;
      api->free_context(&ctx);
    }
    RIME_STRUCT(RimeCommit, commit);
    if (api->get_commit(session, &commit)) {
      std::cout << "\tCOMMIT=" << commit.text;
      api->free_commit(&commit);
    }
    std::cout << std::endl;
  }
  api->destroy_session(session);
  api->finalize();
}
