workflow data_analysis {
    take:
    all_cell_tracks_dataframe
    all_graph_datasets

    main:
    // clear the parent_outdir
    new File(params.parent_outdir).deleteDir()
    new File(params.parent_outdir).mkdirs()

    python_files_ch = Channel.fromPath("${moduleDir}/analysis-scripts/**/*.py", hidden: false)

    execute_python_analysis_script(python_files_ch, all_cell_tracks_dataframe, all_graph_datasets, params.parent_outdir)
}

process execute_python_analysis_script {

    publishDir "${parent_dir_out}/${python_file.baseName}", mode: 'copy'

    label "single_threaded", "short_running"

    conda "${moduleDir}/environment.yml"

    input:
    path python_file
    path all_cell_tracks_dataframe
    val all_graph_datasets
    val parent_dir_out

    output:
    path "*"

    script:
    """
    python ${python_file} \
        --dataframe_file=${all_cell_tracks_dataframe} \
        --parent_dir_out="." \
    """
}
