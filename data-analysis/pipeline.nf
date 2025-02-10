workflow data_analysis {
    take:
    all_cell_tracks_dataframe
    all_graph_datasets

    main:
    // clear the parent_outdir
    new File(params.parent_outdir).deleteDir()
    new File(params.parent_outdir).mkdirs()

    python_files_ch = Channel.fromPath("${workflow.moduleDir}/analysis-scripts/**/*.py", hidden: false)

    execute_python_analysis_script(python_files_ch, all_cell_tracks_dataframe, all_graph_datasets, params.parent_outdir)
}

process execute_python_analysis_script {

    publishDir "${parent_dir_out}/${python_file.baseName}", mode: 'copy'

    input:
    path python_file
    path all_cell_tracks_dataframe
    path all_graph_datasets
    val parent_dir_out

    output:
    path "*"

    script:
    """
    python ${python_file} \
        --complete_dataframe_path=${all_cell_tracks_dataframe} \
        --parent_dir_out="." \
        --cell_class="HeLa_CaSki"
    """
}
